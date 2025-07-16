# Dockerfile for shipping-data-product-week7
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Default command (can be changed as needed)
CMD ["python"]
