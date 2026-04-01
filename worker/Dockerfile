# 1. Start the Base
FROM python:3.12-slim

# 2. Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 3. Set WORKDIR
WORKDIR /app

# 4. Copy worker specific dependencies
COPY pyproject.toml uv.lock ./

# 5. Install LIBS
RUN uv sync --frozen

# 6. Copy the worker code
COPY . .

# 7. Execute
CMD ["uv", "run", "python", "worker.py"]