FROM python:3.12-slim

WORKDIR /app

# System deps needed by faiss/torch wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first so this layer caches between code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Build the FAISS index at image-build time so startup is fast and offline.
# This downloads the ~80MB sentence-transformer model into the image.
RUN python -m rag.build_index

# Streamlit needs to listen on all interfaces, not just localhost
EXPOSE 8501

CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
