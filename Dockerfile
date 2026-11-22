# Multi-stage build for Capstone DevOps Project
# Stage 1: dependencies
FROM python:3.11-slim AS builder

WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: runtime
FROM python:3.11-slim AS runner

RUN groupadd -g 10002 forge && \
    useradd -u 10002 -g forge -m -s /bin/false forgeuser

WORKDIR /app
COPY --from=builder /install /usr/local
COPY app/ /app/
RUN chown -R forgeuser:forge /app

USER 10002:10002

ENV PYTHONUNBUFFERED=1 \
    PORT=5000 \
    APP_ENV=production \
    APP_VERSION=1.4.2 \
    SERVICE_NAME=capstone-devops-api

EXPOSE 5000

HEALTHCHECK --interval=25s --timeout=4s --start-period=8s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health/live')" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "45", "--access-logfile", "-", "main:app"]
