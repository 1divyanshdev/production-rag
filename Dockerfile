# ---- build stage ----
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencies first: this layer is cached unless requirements change
COPY requirements.txt requirements-dev.txt ./
RUN pip install -r requirements.txt

# ---- app ----
COPY backend ./backend
COPY pytest.ini ./

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
