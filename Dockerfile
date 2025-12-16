# Kafka Performance Testing Container
# Includes Kafka CLI tools, Ansible, and Python dependencies for report generation

FROM ubuntu:22.04

LABEL maintainer="OSO DevOps"
LABEL description="Kafka Performance Testing Automation"
LABEL version="1.0"

# Install system dependencies and Java (required for Kafka CLI tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ansible \
    python3 \
    python3-pip \
    python3-venv \
    openjdk-17-jre-headless \
    curl \
    netcat \
    && rm -rf /var/lib/apt/lists/*

# Download and install Kafka CLI tools
ENV KAFKA_VERSION=3.5.1
ENV SCALA_VERSION=2.13
RUN curl -sL "https://archive.apache.org/dist/kafka/${KAFKA_VERSION}/kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz" | tar -xz -C /opt && \
    mv /opt/kafka_${SCALA_VERSION}-${KAFKA_VERSION} /opt/kafka

# Add Kafka binaries to PATH
ENV PATH="/opt/kafka/bin:$PATH"
ENV KAFKA_HOME="/opt/kafka"

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Create virtual environment and install Python dependencies
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Set virtual environment in PATH
ENV PATH="/opt/venv/bin:$PATH"

# Copy application files
COPY . .

# Set environment variables
ENV ANSIBLE_HOST_KEY_CHECKING=False
ENV ANSIBLE_RETRY_FILES_ENABLED=False

# Create results directory
RUN mkdir -p /app/results/raw_logs /app/results/parsed_data /app/results/reports

# Default command - show help
CMD ["ansible-playbook", "--help"]
