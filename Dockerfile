# Multi-stage build for minimal image size
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install PyTorch CPU version first (much smaller than GPU version)
RUN pip install --no-cache-dir --user \
    torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu

# Install remaining Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Pre-download the sentence-transformer model to avoid downloading at runtime
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-base-en-v1.5')"

# Clean up unnecessary cache files to reduce image size
RUN find /root/.cache -type f -name "*.h5" -delete && \
    find /root/.cache -type f -name "*.ot" -delete && \
    find /root/.cache -type f -name "*.msgpack" -delete

# Final stage - minimal runtime image
FROM python:3.11-slim

# Install cloudflared for Cloudflare tunnel
RUN apt-get update && apt-get install -y wget && \
    wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb && \
    apt-get install -y ./cloudflared-linux-amd64.deb && \
    rm cloudflared-linux-amd64.deb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy the pre-downloaded model cache from builder
COPY --from=builder /root/.cache /root/.cache

# Copy application code
COPY . .

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Create directories for logs if needed
RUN mkdir -p logs

# Expose port
EXPOSE 8008

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV CLOUDFLARE_TUNNEL_TOKEN=eyJhIjoiOGJlNWJkYzMzYjZiNDQ0MTI3YjUwMzBlZjQyNTJlZTAiLCJ0IjoiOTI0YmJiOGMtMTE2ZC00ZjVjLWIyY2QtMmYyZTA2ZjU2NDhmIiwicyI6IllqWTJOV1ZpTlRNdE5qQTJZaTAwWTJNNUxUazBPVGd0TkRNME5UUTNPV1prWkdSaiJ9

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8008/', timeout=5)" || exit 1

# Run Flask app and Cloudflare tunnel together
CMD sh -c "python app.py & \
           sleep 10 && \
           cloudflared tunnel --no-autoupdate run --token ${CLOUDFLARE_TUNNEL_TOKEN}"
