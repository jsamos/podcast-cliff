# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app
COPY . ./

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Ensure the container keeps running
CMD ["python", "worker.py"]