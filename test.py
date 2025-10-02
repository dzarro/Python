import threading
import time

stop_flag = False

def worker_function_bool():
    global stop_flag
    while not stop_event.is_set():
        print("Worker thread (bool) is running...")
        time.sleep(1)
    print("Worker thread (bool) stopping.")

# Create and start the worker thread
worker_thread_bool = threading.Thread(target=worker_function_bool)
worker_thread_bool.start()

# Let the worker run for a few seconds
time.sleep(5)

# Signal the worker thread to stop
print("Main thread signaling worker (bool) to stop.")
stop_flag = True

# Wait for the worker thread to finish
worker_thread_bool.join()
print("Main thread finished.")