FROM python:3.11-slim as builder

WORKDIR /app
ENV PATH=/root/.local/bin:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    wget \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


FROM python:3.11-slim

WORKDIR /app
ENV PATH=/root/.local/bin:$PATH

COPY --from=builder /root/.local /root/.local
COPY . .

RUN mkdir -p logs

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py

CMD ["sh", "-c", "gunicorn app:app --worker-class gevent --workers 3 --bind 0.0.0.0:${PORT}"]
