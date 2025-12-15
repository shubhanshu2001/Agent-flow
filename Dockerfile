# ==========================================
# 1. Base Python image
# ==========================================
FROM python:3.11-slim

# Prevent Python from buffering outputs (helps debugging logs)
ENV PYTHONUNBUFFERED=1

# ==========================================
# 2. Set working directory inside container
# ==========================================
WORKDIR /app

# ==========================================
# 3. Install system dependencies
# ==========================================
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ==========================================
# 4. Copy dependency files
# ==========================================
COPY requirements.txt /app/requirements.txt

# ==========================================
# 5. Install Python dependencies
# ==========================================
RUN pip install --no-cache-dir -r /app/requirements.txt

# ==========================================
# 6. Copy your application code
# ==========================================
COPY . /app

# ==========================================
# 7. Expose FastAPI port
# ==========================================
EXPOSE 8000

# ==========================================
# 8. Start server using Uvicorn
# ==========================================
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
