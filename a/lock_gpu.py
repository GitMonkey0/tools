import torch
import time


def occupy_gpu_memory(target_percent=0.9):
    if not torch.cuda.is_available():
        print("未检测到GPU")
        return

    device = torch.device("cuda")
    total_memory = torch.cuda.get_device_properties(device).total_memory
    target_bytes = int(total_memory * target_percent)

    # 采用小块分配策略
    block_size = 256 * 1024 * 1024  # 256MB 的块
    allocated = 0
    chunks = []

    try:
        while allocated < target_bytes:
            # 计算当前要分配的块大小
            remaining = target_bytes - allocated
            current_block = min(block_size, remaining)

            # 分配张量
            elements = current_block // 4  # float32 每个元素4字节
            chunk = torch.empty((elements,), dtype=torch.float32, device=device)
            chunks.append(chunk)
            allocated += current_block

            print(f"已分配 {allocated / (1024 ** 3):.2f}GB / {target_bytes / (1024 ** 3):.2f}GB")

    except torch.cuda.OutOfMemoryError:
        print(f"分配达到极限，最终占用 {allocated / (1024 ** 3):.2f}GB")

    # 保持占用状态
    print(f"GPU显存已占用约 {target_percent * 100:.1f}%")
    while True:
        time.sleep(1)


if __name__ == "__main__":
    occupy_gpu_memory(target_percent=0.9)