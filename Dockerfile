# Base image
FROM python:3.11-slim

# Workdir
WORKDIR /app

# Requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY ./app /app

# Expose
EXPOSE 8000

# Run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
