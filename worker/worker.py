import os 
import time
import redis

REDIS_HOST= os.getenv("REDIS_HOST", "localhost")
REDIS_PORT= int(os.getenv("REDIS_PORT", 6379))

r= redis.Redis(host= REDIS_HOST, port= REDIS_PORT, decode_responses= True)

def process_tasks():
    print(f"Worker connected to Redis at {REDIS_HOST}: {REDIS_PORT}")
    print("Waiting for tasks...")

    while True:
        # BRPOP (Blocking Right POP) will 'wait' here until an order arrives.
        # It's like a chef looking at the order wheel!
        task= r.brpop("task_queue", timeout= 5)

        if task:
            queue_name, message= task
            print(f"[NEW TASK] Received: {message}")

            # SIMULATE HARD WORK
            time.sleep(2)

            print(f"[FINISHED] Done with: {message}")

if __name__ == "__main__":
    process_tasks()