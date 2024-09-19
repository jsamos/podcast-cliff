# Start with the AWS Lambda Python 3.9 base image
FROM public.ecr.aws/lambda/python:3.9

# Install system dependencies and download static ffmpeg
RUN yum update -y && \
    yum install -y libatomic wget tar xz && \
    wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz && \
    tar xvf ffmpeg-release-amd64-static.tar.xz && \
    mv ffmpeg-*-amd64-static/ffmpeg /usr/local/bin/ && \
    rm -rf ffmpeg-*-amd64-static* && \
    yum remove -y wget tar xz && \
    yum clean all && \
    rm -rf /var/cache/yum

# Set the working directory
WORKDIR /var/task

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Set the Lambda entry point to the handler function
CMD ["worker.lambda_handler"]

# For testing: verify ffmpeg and Python dependencies (remove for production)
RUN ffmpeg -version && pip list
