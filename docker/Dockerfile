FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    gperf \
    libssl-dev \
    zlib1g-dev \
    portaudio19-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Build TDLib
COPY scripts/build_tdlib.sh /app/scripts/
RUN chmod +x /app/scripts/build_tdlib.sh && \
    /app/scripts/build_tdlib.sh

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directories
RUN mkdir -p data/recordings data/transcripts data/temp logs

# Run the assistant
CMD ["python", "src/main.py"]