from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import Callable, Iterable, Any, List, Dict, Tuple, Optional
import time


def run_concurrently(
        tasks: Iterable[Dict[str, Any]],
        max_workers: int = 4,
        use_processes: bool = False,
        validation_func: Optional[Callable[[Any], bool]] = None  # 可选的自定义检验函数
) -> List[Any]:
    """
    并行执行多个任务，每个任务可以有不同的函数和参数，并保持结果顺序与输入任务一致。
    失败的任务会无限重试，直到成功为止。如果提供了验证函数且验证失败，则重新执行任务。

    :param tasks: 一个可迭代对象，每个元素是一个字典，包含 'func' 和 'args'/'kwargs'。
                 示例:
                 [
                     {'func': func1, 'args': (arg1, arg2), 'kwargs': {'kwarg1': value1}},
                     {'func': func2, 'args': (argA,), 'kwargs': {}},
                 ]
    :param max_workers: 最大工作线程/进程数
    :param use_processes: 是否使用进程池，默认为线程池
    :param validation_func: 可选的自定义检验函数，用于验证任务结果是否有效。如果返回False，则重新执行任务。
    :return: 任务执行结果的列表，顺序与输入任务列表一致
    """
    Executor = ProcessPoolExecutor if use_processes else ThreadPoolExecutor

    # 将任务转换为 (index, task) 的形式，以便后续排序
    indexed_tasks = list(enumerate(tasks))
    results = [None] * len(indexed_tasks)
    total_tasks = len(indexed_tasks)
    last_print_time = 0
    print_interval = 5  # 每5秒打印一次进度

    with Executor(max_workers=max_workers) as executor:
        # 提交所有任务
        futures = {}
        for idx, task in indexed_tasks:
            func = task['func']
            args = task.get('args', ())
            kwargs = task.get('kwargs', {})

            # 提交任务，并将 future 与索引关联
            future = executor.submit(func, *args, **kwargs)
            futures[future] = idx

        # 按完成顺序处理任务，但按原始索引存储结果
        while futures:
            current_time = time.time()
            # 每隔print_interval秒打印一次进度
            if current_time - last_print_time >= print_interval:
                completed = sum(1 for r in results if r is not None)
                remaining = total_tasks - completed
                print(f"Progress: {completed}/{total_tasks} completed, {remaining} remaining")
                last_print_time = current_time

            # 等待任意一个任务完成
            done, _ = as_completed(futures), None
            for future in done:
                idx = futures.pop(future)
                try:
                    result = future.result()
                    # 如果提供了验证函数且验证失败，则重新执行任务
                    if validation_func is not None and not validation_func(result):
                        print(f"Validation failed for task {idx}, retrying...")
                        task = indexed_tasks[idx][1]
                        future = executor.submit(task['func'], *task.get('args', ()), **task.get('kwargs', {}))
                        futures[future] = idx
                    else:
                        results[idx] = result
                except Exception as e:
                    print(f"Error processing task {idx}: {e}")
                    # 重新提交失败的任务
                    task = indexed_tasks[idx][1]
                    future = executor.submit(task['func'], *task.get('args', ()), **task.get('kwargs', {}))
                    futures[future] = idx

    # 按原始任务顺序返回结果
    return [result for _, result in sorted(zip([idx for idx, _ in indexed_tasks], results))]