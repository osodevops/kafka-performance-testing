# Offline/Air-Gapped Installation Guide

This guide explains how to install and run the Kafka Performance Testing framework in air-gapped environments without internet access.

## Overview

Air-gapped environments require all dependencies to be pre-downloaded and transferred manually. This guide covers:

1. Downloading packages on an internet-connected machine
2. Transferring to the air-gapped environment
3. Installing and running tests offline

---

## Step 1: Download Packages (Internet-Connected Machine)

On a machine with internet access:

### Option A: Use the Download Script

```bash
# Clone the repository
git clone https://github.com/osodevops/kafka-performance-testing.git
cd kafka-performance-testing

# Make script executable
chmod +x scripts/download_offline_packages.sh

# Download all packages
./scripts/download_offline_packages.sh
```

### Option B: Manual Download

```bash
# Create directory for offline packages
mkdir -p offline_packages

# Download Python packages
pip3 download -r requirements.txt -d offline_packages/

# Download pip/setuptools/wheel for bootstrapping
pip3 download pip setuptools wheel -d offline_packages/
```

### Downloaded Packages

The following packages will be downloaded:

| Package | Purpose |
|---------|---------|
| openpyxl | Excel report generation |
| et-xmlfile | XML handling for Excel |
| numpy | Statistical calculations |
| pandas | Data manipulation |
| python-dateutil | Date parsing |
| pytz | Timezone handling |
| six | Python 2/3 compatibility |

---

## Step 2: Download Docker Images (If Using Docker)

If you plan to use Docker Compose, save the required images:

```bash
# Pull and save images
docker pull confluentinc/cp-zookeeper:7.5.0
docker pull confluentinc/cp-kafka:7.5.0
docker pull provectuslabs/kafka-ui:latest

# Save to tar files
docker save confluentinc/cp-zookeeper:7.5.0 -o offline_packages/cp-zookeeper-7.5.0.tar
docker save confluentinc/cp-kafka:7.5.0 -o offline_packages/cp-kafka-7.5.0.tar
docker save provectuslabs/kafka-ui:latest -o offline_packages/kafka-ui-latest.tar
```

---

## Step 3: Transfer to Air-Gapped Environment

Transfer the following to your air-gapped environment:

```
kafka-performance-testing/
├── offline_packages/          # All downloaded packages
│   ├── *.whl                  # Python wheel files
│   ├── *.tar.gz               # Python source packages
│   └── *.tar                  # Docker images (if using Docker)
├── ansible_collections/       # Ansible playbooks and roles
├── scripts/                   # Python scripts
├── inventories/               # Ansible inventories
├── requirements.txt           # Python requirements
├── docker-compose.yml         # Docker Compose config
└── ...                        # Other project files
```

Transfer methods:
- USB drive
- Secure file transfer
- Burned media (CD/DVD)
- Network transfer through data diode

---

## Step 4: Install in Air-Gapped Environment

### 4.1 Create Virtual Environment

```bash
cd kafka-performance-testing

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows
```

### 4.2 Install Python Packages Offline

```bash
# Upgrade pip first (from offline packages)
pip install --no-index --find-links=offline_packages/ --upgrade pip setuptools wheel

# Install all requirements
pip install --no-index --find-links=offline_packages/ -r requirements.txt
```

### 4.3 Verify Installation

```bash
# Check packages are installed
pip list

# Test the Excel generator
python -c "import openpyxl; print('openpyxl:', openpyxl.__version__)"
python -c "import pandas; print('pandas:', pandas.__version__)"
```

---

## Step 5: Load Docker Images (If Using Docker)

If you're using the Docker Compose setup:

```bash
# Load saved images
docker load -i offline_packages/cp-zookeeper-7.5.0.tar
docker load -i offline_packages/cp-kafka-7.5.0.tar
docker load -i offline_packages/kafka-ui-latest.tar

# Verify images are loaded
docker images | grep -E "(cp-zookeeper|cp-kafka|kafka-ui)"
```

---

## Step 6: Configure and Run Tests

### Option A: Against Existing Kafka Cluster

Configure your inventory to point to your Kafka cluster:

```bash
# Edit inventory
vi inventories/dev/hosts.yml
```

```yaml
all:
  hosts:
    kafka-broker-1:
      ansible_host: your-broker-1.internal
      broker_id: 0
  vars:
    kafka_broker:
      hosts:
        - your-broker-1.internal:9092
        - your-broker-2.internal:9092
        - your-broker-3.internal:9092
```

Run tests:

```bash
ansible-playbook -i inventories/dev \
  ansible_collections/oso/test/playbooks/producer_baseline.yml
```

### Option B: Using Local Docker Cluster

Start the local cluster (images must be pre-loaded):

```bash
# Start cluster
docker-compose up -d

# Enter test container
docker exec -it kafka-perf-test bash

# Run tests
ansible-playbook -i inventories/local \
  ansible_collections/oso/test/playbooks/producer_baseline.yml
```

---

## Step 7: Generate Reports Offline

Reports are generated automatically after tests. To manually generate:

```bash
# Activate virtual environment
source venv/bin/activate

# Generate Excel report
python scripts/generate_excel_report.py \
  ./results/parsed_data/parsed_results_*.json \
  ./results/reports/kafka_perf_report.xlsx \
  --verbose
```

---

## Troubleshooting

### Package Installation Fails

If `pip install` fails with missing dependencies:

```bash
# List what's in offline_packages
ls offline_packages/

# Check for the specific package
ls offline_packages/ | grep -i <package_name>
```

Ensure all packages were downloaded on the same Python version and OS as the target.

### Platform Mismatch

Python wheels are platform-specific. If you see errors like "not a supported wheel":

1. Download packages on the same OS/architecture as the target
2. Or use source distributions:

```bash
# Download source packages (more portable)
pip3 download -r requirements.txt -d offline_packages/ --no-binary :all:
```

### Docker Image Load Fails

```bash
# Check image file integrity
file offline_packages/*.tar

# Load with verbose output
docker load -i offline_packages/cp-kafka-7.5.0.tar --quiet=false
```

---

## Multi-Platform Support

To support multiple platforms (Linux, macOS, Windows), download packages for each:

```bash
# Linux x86_64
pip3 download -r requirements.txt -d offline_packages/linux_x86_64/ \
  --platform manylinux2014_x86_64 --only-binary=:all:

# macOS ARM64
pip3 download -r requirements.txt -d offline_packages/macos_arm64/ \
  --platform macosx_11_0_arm64 --only-binary=:all:

# Windows x86_64
pip3 download -r requirements.txt -d offline_packages/windows_x86_64/ \
  --platform win_amd64 --only-binary=:all:
```

---

## Quick Reference

```bash
# Download (internet-connected)
./scripts/download_offline_packages.sh

# Install (air-gapped)
source venv/bin/activate
pip install --no-index --find-links=offline_packages/ -r requirements.txt

# Verify
python -c "import openpyxl, pandas; print('OK')"

# Run tests
ansible-playbook -i inventories/dev \
  ansible_collections/oso/test/playbooks/producer_baseline.yml
```
