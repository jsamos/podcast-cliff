# Stage 1: Build the base image using python:3.9-slim to install dependencies
FROM python:3.9-slim AS build

# Set the working directory
WORKDIR /app

# Install system dependencies (ffmpeg and libatomic1)
RUN apt-get update && apt-get install -y ffmpeg libatomic1

# Copy requirements.txt and install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Stage 2: Start with the AWS Lambda Python 3.9 base image
FROM public.ecr.aws/lambda/python:3.9

# Copy installed dependencies from the build stage
COPY --from=build /app /var/task

# Set the Lambda entry point to the handler function (adjust this to your handler)
CMD ["worker.lambda_handler"]
