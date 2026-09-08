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

# Hugging Face Spaces & Cloud containers use PORT
ENV PORT=7860
EXPOSE 7860

CMD ["python", "template_studio.py"]
