#!/bin/bash

# 默认参数配置
MEMORY_THRESHOLD=8000        # 显存使用阈值(MB)
NEEDED_GPUS=3                # 需要的GPU数量
OCCUPY_SCRIPT="1.py"         # 占卡脚本路径
TRAIN_COMMAND="llamafactory-cli train examples/train_full/qwen2.5_full_sft_1e-5.yaml"
CHECK_INTERVAL=5             # 监控频率(秒)

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case "$1" in
        -t|--threshold)
            MEMORY_THRESHOLD="$2"
            shift 2
            ;;
        -n|--needed-gpus)
            NEEDED_GPUS="$2"
            shift 2
            ;;
        -o|--occupy-script)
            OCCUPY_SCRIPT="$2"
            shift 2
            ;;
        -c|--train-command)
            TRAIN_COMMAND="$2"
            shift 2
            ;;
        -i|--check-interval)
            CHECK_INTERVAL="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  -t, --threshold     显存使用阈值(MB) (默认: 8000)"
            echo "  -n, --needed-gpus   需要的GPU数量 (默认: 3)"
            echo "  -o, --occupy-script 占卡脚本路径 (默认: 1.py)"
            echo "  -c, --train-command 训练命令 (默认: llamafactory-cli train...)"
            echo "  -i, --check-interval 监控频率(秒) (默认: 5)"
            echo "  -h, --help          显示帮助信息"
            exit 0
            ;;
        *)
            echo "未知参数: $1"
            exit 1
            ;;
    esac
done

# 全局状态记录
declare -A OCCUPY_PIDS       # 占卡进程PID记录(gpu_index: pid)
OCCUPIED_LIST=()             # 已占用的GPU索引数组

# 优雅退出处理
trap cleanup EXIT

function cleanup() {
    echo "执行清理..."
    # 杀死所有占卡进程
    for gpu_index in "${!OCCUPY_PIDS[@]}"; do
        kill -9 "${OCCUPY_PIDS[$gpu_index]}" 2>/dev/null
        echo "释放GPU $gpu_index (PID: ${OCCUPY_PIDS[$gpu_index]})"
    done
}

function get_free_gpus() {
    # 获取当前空闲GPU列表(未被占用且显存低于阈值)
    nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits 2>/dev/null | \
    awk -F', ' -v threshold="$MEMORY_THRESHOLD" \
    '$2 < threshold && !($1 in occupied) {print $1}' occupied=$(IFS=,; echo "${!OCCUPY_PIDS[*]}") | \
    sort -n
}

function occupy_gpu() {
    local gpu_index=$1
    echo "正在占用GPU $gpu_index..."
    CUDA_VISIBLE_DEVICES=$gpu_index python "$OCCUPY_SCRIPT" &
    local pid=$!
    OCCUPY_PIDS["$gpu_index"]=$pid
    OCCUPIED_LIST+=("$gpu_index")
    echo "GPU $gpu_index 占用成功(PID: $pid)"
}

function start_training() {
    local selected_gpus=$(IFS=,; echo "$*")
    echo "满足条件，在GPU $selected_gpus 上启动训练..."

    cleanup  # 先释放所有占卡进程

    # 启动训练任务
    CUDA_VISIBLE_DEVICES="$selected_gpus" $TRAIN_COMMAND

    exit 0  # 训练完成后退出脚本
}

function random_select_gpus() {
    local gpu_list=($@)
    local available_count=${#gpu_list[@]}
    local selected=()

    # 随机选择NEEDED_GPUS个GPU
    for ((i=0; i<$NEEDED_GPUS; i++)); do
        local random_idx=$((RANDOM % available_count))
        selected+=("${gpu_list[$random_idx]}")
        # 从列表中移除已选择的GPU
        unset "gpu_list[$random_idx]"
        gpu_list=("${gpu_list[@]}")
        ((available_count--))
    done

    echo "${selected[@]}"
}

# 主监控循环
while true; do
    # 获取当前空闲GPU
    free_gpus=($(get_free_gpus))
    free_count=${#free_gpus[@]}

    # 情况1：已有足够占用的GPU
    if [ ${#OCCUPIED_LIST[@]} -ge $NEEDED_GPUS ]; then
        start_training "${OCCUPIED_LIST[@]:0:$NEEDED_GPUS}"

    # 情况2：当前空闲GPU足够
    elif [ $free_count -ge $NEEDED_GPUS ]; then
        selected=($(random_select_gpus "${free_gpus[@]}"))
        start_training "${selected[@]}"

    # 情况3：需要继续占卡
    else
        # 占用所有可用空闲GPU
        for gpu_index in "${free_gpus[@]}"; do
            if [ -z "${OCCUPY_PIDS[$gpu_index]}" ]; then
                occupy_gpu "$gpu_index"
            fi
        done

        echo "当前占用GPU: [${OCCUPIED_LIST[*]}]，还需占用: $((NEEDED_GPUS - ${#OCCUPIED_LIST[@]}))张"
    fi

    sleep $CHECK_INTERVAL
done