import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from tqdm.asyncio import tqdm_asyncio

async def execute(func, params_list, max_workers=8):
    """支持字典传参的并发执行器"""
    pool = ThreadPoolExecutor(max_workers)
    
    async def run(params):
        while True:
            try:
                if isinstance(params, dict):
                    # 字典参数调用
                    return await asyncio.get_event_loop().run_in_executor(
                        pool, lambda: func(**params)
                    )
                else:
                    # 元组参数调用
                    return await asyncio.get_event_loop().run_in_executor(
                        pool, func, *params
                    )
            except Exception as e:
                print(f"Error in {func.__name__}: {e}, retrying...")
                await asyncio.sleep(1)

    tasks = [run(params) for params in params_list]
    return await tqdm_asyncio.gather(*tasks, desc=func.__name__)

def run(func, params_list, max_workers=8):
    """同步调用入口"""
    return asyncio.run(execute(func, params_list, max_workers))

# 测试函数（带默认参数）
def mock_io_request(a, b=10, c=20):
    time.sleep(0.5)  # 模拟I/O延迟
    return a + b + c

if __name__ == "__main__":
    # 参数列表（混合元组和字典传参）
    test_params = [
        (1, 2),              # 位置参数 a=1, b=2, c=20(默认)
        {"a": 3, "c": 30},   # 跳过b，使用默认值b=10
        {"a": 4, "b": 5},    # 跳过c，使用默认值c=20
        (5,),                # 仅a，使用默认值b=10, c=20
        (6, 7, 8),           # 所有位置参数
        {"a": 9, "b": 1, "c": 2}  # 全字典参数
    ]
    
    print("▶️ 开始并发测试（字典传参版）")
    start_time = time.time()
    results = run(mock_io_request, test_params, max_workers=4)
    elapsed = time.time() - start_time

    print("\n📋 执行结果：")
    print(results)  # [23, 43, 29, 35, 21, 12]
    
    print("\n🔍 性能报告：")
    print(f"总任务数: {len(test_params)}")
    print(f"总耗时: {elapsed:.2f}秒")
    print(f"吞吐量: {len(test_params)/elapsed:.2f} 任务/秒")