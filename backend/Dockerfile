# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY req.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r req.txt

# Copy the rest of the application
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the app
CMD ["uvicorn", "chat:app", "--host", "0.0.0.0", "--port", "8000"]