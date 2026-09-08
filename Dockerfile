FROM python:3.10-slim

# Install system dependencies (ffmpeg is required for video compositing)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Cloud platforms like Railway and Render set the PORT environment variable
ENV PORT=8080
EXPOSE 8080

CMD ["python", "template_studio.py"]
