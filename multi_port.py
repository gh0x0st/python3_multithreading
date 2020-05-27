#!/usr/bin/python3

import threading        # https://docs.python.org/3/library/threading.html
import queue            # https://docs.python.org/3/library/queue.html
import time             # https://docs.python.org/3/library/time.html
import socket           # https://docs.python.org/3/library/socket.html


def worker():
    while True:
        port = q.get()
        scan_port(target, port)
        q.task_done()


def scan_port(target, port):
    try:
        # create stream socket with a one second timeout and attempt a connection
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((target, int(port)))

        # disallow further sends and receives
        s.shutdown(socket.SHUT_RDWR)
        with thread_lock:
            print(f'[+] Port {port} on {target} is OPEN')
    except ConnectionRefusedError:
        pass
    finally:
        s.close()

# Device to scan
target = '192.168.74.131'

# Define a print lock
thread_lock = threading.Lock()

# Create our queue
q = queue.Queue()

# Define number of threads
for r in range(100):
    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()

# Start timer before sending tasks to the queue
start_time = time.time()

print('Creating a task request for each port\n')

# Create a task request for each possible port to the worker
for port in range(1, 65535):
    q.put(port)

# block until all tasks are done
q.join()

print(f"\nAll workers completed their tasks after {round(time.time() - start_time, 2)} seconds")
