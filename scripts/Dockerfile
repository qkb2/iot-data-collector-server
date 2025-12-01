FROM python:3.11-slim

WORKDIR /app

# Install requests
RUN pip install --no-cache-dir requests

# Copy script
COPY simulate_devices.py .

ENTRYPOINT ["python", "simulate_devices.py"]
CMD ["--interval", "1"]
