FROM python:3.11-slim as builder

WORKDIR /app

ENV PATH=/root/.local/bin:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    wget \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install PyTorch CPU version first (much smaller than GPU version)
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local

COPY --from=builder /root/.cache /root/.cache

# Copy application code
COPY . .

ENV PATH=/root/.local/bin:$PATH

RUN mkdir -p logs

EXPOSE 8008

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV RUN_TUNNEL=false

CMD ["gunicorn", "--worker-class", "gevent", "--workers", "3", "--bind", "0.0.0.0:8008", "app:app"]
