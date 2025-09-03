import multiprocessing
import time


def calculate_chunk(start_end):
    start, end = start_end
    return (end - start + 1) * (start + end) // 2


def calculate_sum(n=10 ** 13, num_processes=4):
    chunk_size = n // num_processes
    ranges = [(i * chunk_size + 1, (i + 1) * chunk_size if i != num_processes - 1 else n)
              for i in range(num_processes)]

    start_time = time.time()

    with multiprocessing.Pool(num_processes) as pool:
        results = pool.map(calculate_chunk, ranges)

    total = sum(results)

    print(f"Multiprocessing 结果: {total}")
    print(f"耗时: {time.time() - start_time:.6f} 秒")


if __name__ == '__main__':
    calculate_sum()