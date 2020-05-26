#!/usr/bin/python3

import threading        # https://docs.python.org/3/library/threading.html
import queue            # https://docs.python.org/3/library/queue.html
import time             # https://docs.python.org/3/library/time.html


def worker():
    while True:
        item = q.get()
        with thread_lock:
            print(f'Working on {item}')
            print(f'Finished {item}')
        time.sleep(1)
        q.task_done()


# Define a thread lock
thread_lock = threading.Lock()

# Create our queue
q = queue.Queue()

# Define number of threads
for r in range(2):
    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()

# Start timer before sending tasks to the queue
start_time = time.time()

print(f"Creating a task request for each item in the given range\n")

# send ten task requests to the worker
for item in range(10):
    q.put(item)

# block until all tasks are done
q.join()

print(f"All workers completed their tasks after {round(time.time() - start_time, 2)} seconds")
