import threading
import time


def calculate_chunk(start, end, result, index):
    result[index] = (end - start + 1) * (start + end) // 2


def calculate_sum(n=10 ** 13, num_threads=4):
    chunk_size = n // num_threads
    result = [0] * num_threads
    threads = []

    start_time = time.time()

    for i in range(num_threads):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i != num_threads - 1 else n
        t = threading.Thread(target=calculate_chunk, args=(start, end, result, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    total = sum(result)

    print(f"Threading 结果: {total}")
    print(f"耗时: {time.time() - start_time:.6f} 秒")


calculate_sum()