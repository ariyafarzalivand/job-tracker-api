FROM python:3.13-slim

# Do not write .pyc files, and print logs immediately instead of buffering.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements first. Docker caches this layer, so dependencies
# are only reinstalled when requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Development server. A production setup would use gunicorn instead.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]