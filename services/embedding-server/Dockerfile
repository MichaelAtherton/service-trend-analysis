# BERTrend Embedding Server Dockerfile
# GPU-optimized container for semantic embeddings

FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install BERTrend and dependencies
RUN pip install --no-cache-dir \
    bertrend @ git+https://github.com/rte-france/BERTrend.git@v0.1.0 \
    sentence-transformers \
    torch

# Copy configuration
COPY config/ ./config/
COPY start_server.py ./

# Create non-root user
RUN useradd -m -u 1000 embeduser && \
    chown -R embeduser:embeduser /app

USER embeduser

# Expose embedding server port
EXPOSE 8765

# Start embedding server
CMD ["python", "start_server.py"]

