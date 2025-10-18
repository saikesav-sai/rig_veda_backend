# Multi-stage build for minimal image size
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Add .local/bin to PATH to avoid pip warnings
ENV PATH=/root/.local/bin:$PATH

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

# Set environment to disable ONNX and OpenVINO downloads
ENV SENTENCE_TRANSFORMERS_HOME=/root/.cache/torch/sentence_transformers
ENV TRANSFORMERS_OFFLINE=0
ENV HF_HUB_DISABLE_TELEMETRY=1

# Download ONLY safetensors model files using huggingface_hub
# This avoids downloading ONNX, OpenVINO, and other variants
RUN python -c "from huggingface_hub import snapshot_download; \
    import os; \
    os.makedirs('/root/.cache/torch/sentence_transformers', exist_ok=True); \
    snapshot_download( \
        repo_id='sentence-transformers/all-MiniLM-L6-v2', \
        cache_dir='/root/.cache/huggingface', \
        local_dir='/root/.cache/torch/sentence_transformers/sentence-transformers_all-MiniLM-L6-v2', \
        local_dir_use_symlinks=False, \
        ignore_patterns=['*.onnx', '*onnx*', '*openvino*', '*.bin', '*.h5', '*.ot', '*.msgpack'] \
    ); \
    print('✅ Model downloaded successfully (safetensors only)')"

# Verify the model loads correctly with safetensors
RUN python -c "from sentence_transformers import SentenceTransformer; \
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device='cpu'); \
    print('✅ Model loaded successfully'); \
    print(f'Model uses: {type(model[0]).__name__}')"

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

# Copy the pre-downloaded model cache from builder (only safetensors)
COPY --from=builder /root/.cache /root/.cache

# Copy application code
COPY . .

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH
ENV SENTENCE_TRANSFORMERS_HOME=/root/.cache/torch/sentence_transformers

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
CMD sh -c "gunicorn --worker-class gevent --workers 1 --bind 0.0.0.0:8008 app:app & \
           sleep 10 && \
           cloudflared tunnel --no-autoupdate run --token ${CLOUDFLARE_TUNNEL_TOKEN}"
