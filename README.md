# Multithreading tasks using python 3
As you start to get more exposure with penetration testing, you're going to find out real quick that time is precious. You could spend hours on trivial tasks and at some point you're going to want to find ways to become more efficient by automating some of your workflows.

To help myself overcome the barrier of time, I decided to do a deep dive to get more comfortable with using python. As efficient as this language is, eventually I wanted to learn how to incorporate multithreading to make my instructions run even faster. 

## Disclaimer

This repository and the data provided has been created purely for the purposes of academic research and for the development of effective security techniques and is not intended to be used to attack systems except where explicitly authorized. It is your responsibility to obey all applicable local, state and federal laws. 

Project maintainers assume no liability and are not responsible for any misuse or damage caused by the data therein.

## Sections:

1. What is a worker function?
2. What is a queue?
3. What is a thread?
4. Multithreaded Ping Sweep
5. Multithreaded Port Scanner 

## What is a worker function?
A worker function is the set of instructions you define to be run within each thread for every task in the queue. It could be an all-inclusive function, or can even contain other functions you define. Within this function, you need to grab a task from the queue which is how your worker is going to know each unique task it needs to complete. After you're finished, you gracefully tell the queue you're done with that task.

When you write your series of instructions for a threaded operation, you need to guard against simultaneous access to an object. In the snippet below, the shared object is the item variable. If you do not use a lock, what will happen a script that uses a lot of threads might stumble upon each other and cause data corruption, or inaccurate output. This can be helpful in cases where you add mathematical computations in your logic as well.


```python
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
 ```

## What is a queue?
A queue provides a logical means to run a sequence of tasks in an organized manner, which is very useful when incorporated with threaded programs. You create your queue and fill it with tasks. For example, your script could be targeting a list of IP addresses so you fill your queue with IPs. When your worker function runs, it will grab an IP from the queue and will execute its series of instructions. Keep in mind that for every thread you have, that is how many tasks will be running at a time.

* One Thread  = One task at a time until the queue is empty
* Two Threads = Two task at a time until the queue is empty
* Ten Threads = Ten task at a time until the queue is empty

Don't forget the importance of q.join(). This will instruct the main thread to wait until all the tasks are complete before moving on. This is an important piece of information. If you don't put this in place then after you create your queue and start your work, the main thread will end, killing every running task without giving them time to finish.

```python
# Create our queue
q = queue.Queue()

# send ten task requests to the worker
for item in range(10):
    q.put(item)

# block until all tasks are done
q.join()
```

## What is a thread?
A thread on its own is a consolidated set of instructions. With a single thread, one command runs at a time, such as a simple script. When you introduce more threads, or multithreading, you can have multiple series of instructions running at the time same for simultaneous execution. 

For example, let's say you have a script that sends four ICMP probes to two servers and it takes two seconds to probe each server. In this case, the entire processing time in a single thread takes four seconds. Might not sound like a big deal, but when you're scanning a /24 network that can take some time. Especially when you start talking about /16 or a /8. When you introduce two threads, with each thread probing one server, it'll take two seconds to probe both servers because tasks are running simultaneously 

While it sounds like the more threads you throw at a queue the faster your task will complete, however, keep in mind that this is not always true. You need to ensure your system can handle the resources that are being provisioned, especially if your system is already processing other tasks within the script and outside.

```python
# Define number of threads
for r in range(2):
    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()
```

## Skeleton Script
Let's put the above narrative into functional code. As we can see with Python, it's very easy to create yourself a basic structure for a multithreaded process.

**Let's summarize:**

* You create a worker function with your set of instructions
* You define the number of threads you want to provision
* You send the job requests to the queue based on the tasks you want to run
* You wait for the jobs to finish and end your script

Take the time to increase the number of threads and tasks and see how it changes the output. I also added a sleep to the worker function so you can simulate the time it takes for one task to complete.

![Alt text](https://github.com/gh0x0st/python3_multithreading/blob/master/Screenshots/threader.png?raw=true "Default Threader")

```python
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

```

## Penetration Testing Examples
Once you learn how to create multithreaded operations in python, your imagination is the limit. While not everything needs the extra acceleration, you may find it helpful from time to time. Here are two ways you can use multithreading to accelerate penetration testing tasks, with ping sweeps and port scanning.

### Ping Sweep
At one point or another during a pen test, you're going to need to discover live hosts on a network and one of the more efficient ways is to simply send out ICMP probes a see who responds back.

When we're talking about a /24 network, this won't be too difficult. However, when you start talking about a /16 or even a /8, you're going to be running against the clock as we mentioned previously.

To incorporate multithreading in this example, we're going to create tasks by filling the queue with a list of IP addresses and each thread will be used to ping one ip from the queue at a time.

```python
#!/usr/bin/python3

import threading        # https://docs.python.org/3/library/threading.html
import queue            # https://docs.python.org/3/library/queue.html
import ipaddress        # https://docs.python.org/3/library/ipaddress.html
import subprocess       # https://docs.python.org/3/library/subprocess.html
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

``` 

### Port Scanner
Our previous example showed how we can speed up a ping sweep by filling our queue with ip addresses to target. Here, we'll use a slightly different approach by filling our queue with ports we want to scan against a single target. 

Keep in mind that using this socket connect method, it's going to attempt a complete tcp three way handshake, which is where the multithreading can help save us some time. However, having too many threads at time could cause performance issues (miss open ports) or even flag a SIEM or IPS, so find a happy balance with what you're trying to accomplish. 

```python
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

```

What we went through barely touches the surface and there are many other techniques available and more in depth information on what we summarized here. However, this is how I was able to grasp the concepts and hope that you found it useful as well.

## Resources
* https://docs.python.org/3/library/threading.html
* https://docs.python.org/3/library/queue.html
* https://docs.python.org/3/library/socket.html
