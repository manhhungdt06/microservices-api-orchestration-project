FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY ../common/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies for catalog service
RUN pip install --no-cache-dir motor

# Copy service code
COPY ./src /app/src

# Set environment variables
ENV PYTHONPATH=/app
ENV MODULE_NAME=src.main
ENV VARIABLE_NAME=app
ENV PORT=8002

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8002"]
