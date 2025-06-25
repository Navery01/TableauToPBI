# Use official Python image as base
FROM python:3.13.1-slim

# Set working directory
WORKDIR /app

# Copy requirements if available
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set default command (adjust as needed)
CMD ["python", "main.py"]