# 1. Start with a Base
FROM python:3.12-slim

# 2. Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 3. Set WORKDIR
WORKDIR /app

# 4. Copy dependencies first (for speed)
COPY pyproject.toml uv.lock ./

# 5. Install LIBS
RUN uv sync --frozen

# 6. Copy Code
COPY . .

# 7. Execute
CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]