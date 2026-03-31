import os
import redis
from fastapi import FastAPI

app= FastAPI(title= "K8s Microservices Lab")

REDIS_HOST= os.getenv("REDIS_HOST", "localhost")
REDIS_PORT= int(os.getenv("REDIS_PORT", 6379))

# INITIALIZE REDIS
r= redis.Redis(host= REDIS_HOST, port= REDIS_PORT, decode_responses= True)

@app.get("/health")
def health_check():
    """Confirms the API and Redis Connection are healthy."""
    try:
        r.ping()
        return{"status": "healthy", "redis": "connected"}
    except Exception as e:
        return{"status": "unhealthy", "redis": str(e)}

@app.post("/tasks")
def create_task(message: str):
    """Pushes a message into the Redis List 'task_queue'."""
    r.lpush("task_queue", message)
    return{"status": "task_received", "message": message}