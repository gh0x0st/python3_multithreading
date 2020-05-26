#!/usr/bin/python3

import threading        # https://docs.python.org/3/library/threading.html
import queue            # https://docs.python.org/3/library/queue.html
import ipaddress        # https://docs.python.org/3/library/ipaddress.html
import subprocess        # https://docs.python.org/3/library/subprocess.html
import time             # https://docs.python.org/3/library/time.html


def worker():
    while True:
        target = q.get()
        send_ping(target)
        q.task_done()


def send_ping(target):
    icmp = subprocess.Popen(['ping', '-c', '1', str(target)], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    with thread_lock:
        if "1 received" in icmp[0].decode('utf-8'):
            print(f"[*] {target} is UP")
        else:
            print(f"[*] {target} is DOWN")


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

# Network to scan
cidr_network = '192.168.74.0/24'
all_hosts = list(ipaddress.ip_network(cidr_network).hosts())

print(f"Creating a task request for each host in {cidr_network}\n")

# send ten task requests to the worker
for item in all_hosts:
    q.put(item)

# block until all tasks are done
q.join()

print(f"\nAll workers completed their tasks after {round(time.time() - start_time, 2)} seconds")
