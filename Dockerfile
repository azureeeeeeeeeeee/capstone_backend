# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (using Docker-specific requirements)
COPY requirements-docker.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements-docker.txt

# Copy project files
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media /app/exports/classification /app/exports/clustering /app/exports/forecast

# Expose port
EXPOSE 4101

# Run gunicorn
CMD ["gunicorn", "capstone_backend.wsgi:application", "--bind", "0.0.0.0:4101", "--workers", "3"]
