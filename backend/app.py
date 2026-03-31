from fastapi import FastAPI

app= FastAPI(tittle= "K8s Microservices Lab")

@app.get("/health")
def health_check():
    return {"status": "healthy"}