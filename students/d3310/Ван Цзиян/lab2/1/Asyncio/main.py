import asyncio
import time


async def calculate_chunk(start, end):
    return (end - start + 1) * (start + end) // 2


async def calculate_sum(n=10 ** 13, num_tasks=4):
    chunk_size = n // num_tasks
    tasks = []

    start_time = time.time()

    for i in range(num_tasks):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i != num_tasks - 1 else n
        tasks.append(calculate_chunk(start, end))

    results = await asyncio.gather(*tasks)
    total = sum(results)

    print(f"Asyncio 结果: {total}")
    print(f"耗时: {time.time() - start_time:.6f} 秒")


asyncio.run(calculate_sum())