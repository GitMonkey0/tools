#!/bin/bash

# vLLM模型部署脚本
# 用法: 
#   ./deploy_vllm.sh [模型名] [端口号(可选)]  # 部署指定模型
#   ./deploy_vllm.sh cancel                  # 仅停止服务

# 配置区 (根据实际环境修改)
MODEL_DIR="/data/lht/ckpt"            # 模型根目录
LOG_FILE="vllm_server.log"            # 日志文件
DEFAULT_PORT=8000                     # 默认端口
GPU_UTIL=0.9                         # GPU内存利用率
TENSOR_PARALLEL=4                     # 张量并行度

# 模型配置映射 (模型名 -> 模型路径)
declare -A MODEL_MAP=(
    ["Qwen2.5-7B"]="Qwen2.5-7B-Instruct"
    ["Qwen2.5-32B"]="Qwen2.5-32B-Instruct-AWQ"
    ["Qwen2.5-72B"]="Qwen2.5-72B-Instruct-AWQ"
    # 添加更多模型...
)

# 获取参数
OPERATION=${1:-"Qwen2.5-7B"}        # 默认操作是部署Qwen2.5
PORT=${2:-$DEFAULT_PORT}

# 停止服务函数
stop_service() {
    local port=$1
    echo "正在停止服务(端口: $port)..."
    {
        sudo kill -9 $(sudo lsof -t -i :$port 2>/dev/null) &&
        echo "已终止端口 $port 的进程"
    } || echo "未找到占用端口 $port 的进程"
    sleep 1

    pkill -f "python3.12 -c from multiprocessing.spawn" 2>/dev/null &&
    echo "已清理残留子进程" || echo "未找到相关子进程"
    sleep 1

    # 检查端口释放状态
    if lsof -i :$port > /dev/null; then
        echo "警告: 端口 $port 仍被占用，可能被其他进程使用"
        return 1
    fi
    return 0
}

# 如果是cancel操作，只停止服务
if [[ "$OPERATION" == "cancel" ]]; then
    stop_service $PORT
    echo "服务已停止"
    exit 0
fi

# 否则是部署模型操作
MODEL_NAME=$OPERATION

# 检查模型是否存在
if [[ -z "${MODEL_MAP[$MODEL_NAME]}" ]]; then
    echo "错误: 未知模型 '$MODEL_NAME'"
    echo "可用模型: ${!MODEL_MAP[@]}"
    exit 1
fi

MODEL_PATH="$MODEL_DIR/${MODEL_MAP[$MODEL_NAME]}"
if [[ ! -d "$MODEL_PATH" ]]; then
    echo "错误: 模型路径不存在 $MODEL_PATH"
    exit 1
fi

# 先停止服务
if ! stop_service $PORT; then
    exit 1
fi

# 启动服务
echo "正在部署 $MODEL_NAME (路径: $MODEL_PATH)"
echo "配置参数: 端口:$PORT | GPU利用率:$GPU_UTIL | 并行度:$TENSOR_PARALLEL"

nohup bash -c "vllm serve \"$MODEL_PATH\" \
  --tensor-parallel-size $TENSOR_PARALLEL \
  --gpu-memory-utilization $GPU_UTIL \
  --uvicorn-log-level warning \
  --disable-log-requests \
  --max_model_len 10000 \
  --port $PORT" > $LOG_FILE 2>&1 &

# 检查启动状态
for _ in {1..5}; do
    if pgrep -f "vllm serve" > /dev/null; then
        break
    fi
    sleep 1
done

if ! pgrep -f "vllm serve" > /dev/null; then
    echo "启动失败，请检查日志: $LOG_FILE"
    exit 1
fi

# 输出部署信息
cat << EOF

部署成功!
$(printf '%0.s-' {1..40})
模型: \033[32m$MODEL_NAME\033[0m
端口: \033[32m$PORT\033[0m
日志文件: \033[34m$LOG_FILE\033[0m
监控命令:
  • 资源监控: \033[33mwatch -n 1 "nvidia-smi | grep 'Default'\033[0m"
  • 服务状态: \033[33mtail -f $LOG_FILE\033[0m

EOF