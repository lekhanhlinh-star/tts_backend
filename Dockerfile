# 1. Base image: CUDA + Python 3.10
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04
# 2. Install Python 3.10 and pip
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    software-properties-common \
    build-essential \
    git \
    curl \
    ffmpeg \
    default-mysql-client \
    && add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.10 python3.10-venv python3.10-dev python3-pip && \
    ln -sf python3.10 /usr/bin/python && \
    ln -sf pip3 /usr/bin/pip && \
    rm -rf /var/lib/apt/lists/*
# 3. Set working directory
WORKDIR /app
# 4. Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --default-timeout=100 --no-cache-dir -r requirements.txt
# 5. Copy app source
COPY . .
# 6. Make entrypoint executable
RUN chmod +x /app/entrypoint.sh
# 7. Expose port
EXPOSE 8080
# 8. Run entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]