# ☸️ K8s Microservices Lab

A production-grade, cloud-native microservices system built with **FastAPI**, **Redis**, and **Kubernetes**. This lab walks through the full journey: from local development with Docker Compose to a live Kubernetes cluster deployment.

## 🏛️ Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                  Kubernetes Cluster                  │
│                                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────────┐  │
│  │ Backend  │───▶│  Redis   │◀───│    Worker    │  │
│  │ FastAPI  │    │  Queue   │    │  Processor   │  │
│  │ :8000    │    │  :6379   │    │  (bg task)   │  │
│  └──────────┘    └──────────┘    └──────────────┘  │
│       │                                             │
│  NodePort:30000                                     │
└───────┼─────────────────────────────────────────────┘
        │
   Your Browser
  localhost:30000
```

| Service     | Role                              | Image                    |
|-------------|-----------------------------------|--------------------------|
| **Backend** | FastAPI REST API + task publisher  | `karan6124/backend:v1`   |
| **Worker**  | Background task consumer (BRPOP)  | `karan6124/worker:v1`    |
| **Redis**   | In-memory message queue           | `redis:7-alpine`         |

---

## 📁 Project Structure

```
k8s-microservices-lab/
├── backend/
│   ├── app.py               # FastAPI application
│   ├── Dockerfile           # Backend container recipe
│   └── pyproject.toml       # Python dependencies
├── worker/
│   ├── worker.py            # Background task processor
│   ├── Dockerfile           # Worker container recipe
│   └── pyproject.toml       # Python dependencies
├── k8s/
│   ├── redis.yaml           # Redis Deployment
│   ├── services.yaml        # Redis + Backend Services (NodePort)
│   ├── configmap.yaml       # Shared environment config
│   ├── secret.yaml          # Sensitive credentials (Base64)
│   ├── backend-deployment.yaml  # Backend Deployment
│   └── worker-deployment.yaml   # Worker Deployment
├── docker-compose.yml       # Local development orchestration
└── README.md
```

---

## ✅ Prerequisites

Make sure you have these installed before starting:

| Tool             | Purpose                        | Check Command         |
|------------------|--------------------------------|-----------------------|
| **Python 3.12+** | Runtime for services           | `python --version`    |
| **uv**           | Fast Python package manager    | `uv --version`        |
| **Docker Desktop** | Container engine             | `docker --version`    |
| **kubectl**      | Kubernetes CLI                 | `kubectl version`     |

---

## 🚀 Stage 1: Local Development with Docker Compose

### Step 1: Build the Docker Images

```bash
# Build all service images defined in docker-compose.yml
docker compose build
```

**✅ Expected Output:**
```
[+] Building backend ... done
[+] Building worker  ... done
```

**❌ Error: `Cannot connect to the Docker daemon`**
> Docker Desktop is not running. Open Docker Desktop and wait for the engine to start (green icon at the bottom-left).

---

### Step 2: Start All Services

```bash
# Launch Redis, Backend and Worker in the background
docker compose up -d
```

**✅ Expected Output:**
```
✔ Container redis    Started
✔ Container backend  Started
✔ Container worker   Started
```

**❌ Error: `port is already allocated`**
> Another process is using port 6379 or 8000. Stop any conflicting services first:
> ```bash
> docker compose down
> ```

---

### Step 3: Verify Local Health

```bash
# Check running containers
docker compose ps

# Check Backend health
curl http://localhost:8000/health

# View live Worker logs
docker compose logs -f worker
```

**✅ Expected Response from `/health`:**
```json
{ "status": "healthy", "redis": "connected" }
```

---

### Step 4: Stop Local Containers

```bash
# Stop and remove local containers when done
docker compose down
```

---

## ☁️ Stage 2: Push Images to Docker Hub

### Step 5: Tag Your Images

```bash
# Tag the Backend image with your Docker Hub username
docker tag k8s-microservices-lab-backend karan6124/backend:v1

# Tag the Worker image
docker tag k8s-microservices-lab-worker karan6124/worker:v1
```

---

### Step 6: Push Images to Docker Hub

```bash
# Push Backend to the global registry
docker push karan6124/backend:v1

# Push Worker to the global registry
docker push karan6124/worker:v1
```

**✅ Expected Output:**
```
v1: digest: sha256:abc123... size: 856
```

**❌ Error: `denied: requested access to the resource is denied`**
> You are not logged in. Run:
> ```bash
> docker login
> ```
> Then enter your Docker Hub username and password.

---

## ☸️ Stage 3: Kubernetes Deployment

### Step 7: Enable Kubernetes in Docker Desktop

1. Open **Docker Desktop**.
2. Click **Kubernetes** in the left sidebar.
3. Click **"Create cluster"** → Select **"Kubeadm"** → Click **"Create"**.
4. Wait for the cluster status to show **Active** (1-2 minutes).

---

### Step 8: Verify the Cluster is Ready

```bash
kubectl get nodes
```

**✅ Expected Output:**
```
NAME             STATUS   ROLES           AGE
docker-desktop   Ready    control-plane   2m
```

**❌ Error: `couldn't get current server API group list`**
> kubectl is pointing to the wrong cluster context. Fix it:
> ```bash
> # See all available contexts
> kubectl config get-contexts
>
> # Switch to the Docker Desktop cluster
> kubectl config use-context docker-desktop
> ```

---

### Step 9: Deploy Everything to the Cluster

```bash
# Apply ALL manifests in the k8s/ folder at once
kubectl apply -f k8s/
```

**✅ Expected Output:**
```
deployment.apps/backend-deployment  created
deployment.apps/redis-deployment    created
deployment.apps/worker-deployment   created
configmap/microservices-config      created
secret/microservices-secret         created
service/redis                       created
service/backend-service             created
```

---

### Step 10: Watch Pods Come to Life

```bash
# Live watch mode - waits for all pods to reach "Running" state
kubectl get pods -w
```

**✅ Expected Output (wait for all 3 to show "Running"):**
```
NAME                                  READY   STATUS    RESTARTS   AGE
backend-deployment-5b888bfbb-fl26s    1/1     Running   0          21s
redis-deployment-748ffbc5f5-gjwmm     1/1     Running   0          20s
worker-deployment-ff99c54cf-q8fvf     1/1     Running   0          19s
```

**❌ Pod stays in `ImagePullBackOff` or `ErrImagePull`**
> Kubernetes cannot find your Docker image. Check that:
> 1. The image name in the YAML exactly matches what you pushed to Docker Hub.
> 2. You pushed successfully with `docker push karan6124/backend:v1`.

**❌ Pod stays in `CrashLoopBackOff`**
> The container is starting but crashing. Debug with:
> ```bash
> kubectl logs <pod-name>
> # Example:
> kubectl logs backend-deployment-5b888bfbb-fl26s
> ```

---

## 🧪 Testing the Live Cluster

### Step 11: Access the FastAPI Docs

Open your browser and go to:
```
http://localhost:30000/docs
```

### Step 12: Run the Health Check

```bash
curl http://localhost:30000/health
```

**✅ Expected Response:**
```json
{ "status": "healthy", "redis": "connected" }
```

### Step 13: Submit a Task

Using the Swagger UI at `localhost:30000/docs`, call:
```
POST /tasks
Body: { "message": "K8s Mastery Complete!" }
```

### Step 14: Watch the Worker Process the Task

```bash
# Replace with your actual worker pod name from 'kubectl get pods'
kubectl logs -f worker-deployment-ff99c54cf-q8fvf
```

**✅ Expected Output:**
```
Waiting for tasks...
Received task: K8s Mastery Complete!
```

---

## 🛠️ Useful Debugging Commands

```bash
# List all running pods
kubectl get pods

# Get detailed info about a specific pod (useful for crash diagnosis)
kubectl describe pod <pod-name>

# Stream live logs from a pod
kubectl logs -f <pod-name>

# List all services and their ports
kubectl get services

# List all configs and secrets
kubectl get configmaps
kubectl get secrets

# Check current cluster context
kubectl config current-context

# Switch cluster context
kubectl config use-context docker-desktop
```

---

## 🧹 Clean Up

### Remove All Deployments (Keep the Cluster)

```bash
# Deletes all pods, services, and configs but keeps the cluster alive
kubectl delete -f k8s/
```

### Stop the Kubernetes Cluster

In **Docker Desktop** → **Kubernetes** → Click **"Stop"**.

> ℹ️ This saves your computer's RAM. All your YAML blueprints are still on disk — just run `kubectl apply -f k8s/` next time to bring everything back!

---

## 📚 Key Concepts Learned

| Concept | What it Does |
|---|---|
| **Deployment** | Kubernetes "Manager" that keeps pods alive. |
| **Service** | A static IP/DNS address that routes traffic to pods. |
| **ConfigMap** | A shared "Settings Dashboard" for non-sensitive env vars. |
| **Secret** | An encrypted vault for passwords and API keys (Base64 encoded). |
| **NodePort** | Opens a port on the cluster wall for external browser access. |
| **Namespace** | Logical "rooms" that isolate different projects in the same cluster. |
| **`envFrom`** | Injects all ConfigMap values into a container as environment variables. |

---

## 🔑 Environment Variables (via ConfigMap)

| Variable | Value | Used By |
|---|---|---|
| `REDIS_HOST` | `redis` | Backend, Worker |
| `REDIS_PORT` | `6379` | Backend, Worker |

---

*Built with ❤️ by Karan Shelar — from Docker to Kubernetes, one YAML at a time.*
