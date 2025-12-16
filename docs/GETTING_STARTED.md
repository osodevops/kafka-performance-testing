# Getting Started Guide

This guide walks you through setting up and running your first Kafka performance tests.

## 1. Environment Setup

### 1.1 Clone the Repository

```bash
git clone https://github.com/osodevops/kafka-performance-testing.git
cd kafka-performance-testing
```

### 1.2 Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows
```

### 1.3 Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `openpyxl` - Excel report generation
- `pandas` - Data manipulation
- `numpy` - Statistical calculations

### 1.4 Verify Ansible Installation

```bash
ansible --version
# Should be 2.10 or higher
```

If not installed:
```bash
pip install ansible
```

## 2. Local Testing with Docker Compose

For quick local testing without a production Kafka cluster:

### 2.1 Start the Local Kafka Cluster

```bash
# Start 3-broker Kafka cluster
docker-compose up -d

# Wait for all services to be healthy
docker-compose ps

# View logs
docker-compose logs -f
```

This starts:
- **Zookeeper** - Kafka coordination (port 2181)
- **3 Kafka Brokers** - Kafka cluster (ports 9092, 9093, 9094)
- **Kafka UI** - Web monitoring (http://localhost:8080)
- **Perf Test Container** - Test execution environment

### 2.2 Run Tests in the Container

```bash
# Enter the test container
docker exec -it kafka-perf-test bash

# Run a quick producer test
ansible-playbook -i inventories/local \
  ansible_collections/oso/test/playbooks/producer_baseline.yml

# Run full benchmark
ansible-playbook -i inventories/local \
  ansible_collections/oso/test/playbooks/full_benchmark.yml
```

### 2.3 View Results

Results are mounted to `./results/` on your host:
```bash
# On your host machine
ls results/reports/
open results/reports/kafka_perf_report_*.xlsx
```

### 2.4 Stop the Cluster

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

---

## 3. Configure Your Kafka Cluster (Production)

### 3.1 Update Inventory

Edit `inventories/dev/hosts.yml` with your broker details:

```yaml
all:
  hosts:
    kafka-broker-1:
      ansible_host: your-broker-1.example.com
      broker_id: 0
    kafka-broker-2:
      ansible_host: your-broker-2.example.com
      broker_id: 1
    kafka-broker-3:
      ansible_host: your-broker-3.example.com
      broker_id: 2
  vars:
    ansible_user: your-ssh-user
    ansible_ssh_private_key_file: ~/.ssh/your-key
    kafka_broker:
      hosts:
        - your-broker-1.example.com:9092
        - your-broker-2.example.com:9092
        - your-broker-3.example.com:9092
```

### 3.2 Configure Authentication (Optional)

For SSL/SASL clusters, add to `inventories/dev/group_vars/all/defaults.yml`:

```yaml
ssl_enabled: true
kafka_user: "your-username"
kafka_password: "your-password"
```

### 3.3 Verify Connectivity

Test SSH connectivity:
```bash
ansible -i inventories/dev all -m ping
```

Test Kafka connectivity:
```bash
ansible-playbook -i inventories/dev \
  ansible_collections/oso/test/playbooks/produce_consume.yml
```

## 4. Run Your First Test

### 4.1 Basic Connectivity Test

```bash
ansible-playbook -i inventories/dev \
  ansible_collections/oso/test/playbooks/produce_consume.yml
```

This creates a test topic, produces 10 messages, consumes them, and cleans up.

### 4.2 Simple Performance Test

```bash
ansible-playbook -i inventories/dev \
  ansible_collections/oso/test/playbooks/producer_baseline.yml
```

Default quick profile runs with:
- 1 million records
- 1024 byte messages
- acks=1
- zstd compression

### 4.3 Full Benchmark Suite

For comprehensive testing across all scenarios:

```bash
ansible-playbook -i inventories/dev \
  ansible_collections/oso/test/playbooks/full_benchmark.yml
```

## 5. Understanding the Results

### 5.1 Raw Logs

Located in `results/raw_logs/`:

```
producer_baseline_acks1_batch16384_linger10_zstd_size1024_20241216T120000.log
```

Contains raw kafka-producer-perf-test output:
```
1000000 records sent, 14637.645 records/sec (28.59 MB/sec),
3182.27 ms avg latency, 3613.00 ms max latency,
3289 ms 50th, 3467 ms 95th, 3568 ms 99th, 3603 ms 99.9th.
```

### 5.2 Parsed JSON Data

Located in `results/parsed_data/`:

```json
{
  "test_type": "producer",
  "scenario": "baseline",
  "configuration": {
    "acks": "1",
    "batch_size": "16384",
    "linger_ms": "10"
  },
  "metrics": {
    "throughput_mb": 28.59,
    "avg_latency_ms": 3182.27,
    "p99_ms": 3568
  }
}
```

### 5.3 Excel Report Walkthrough

Open `results/reports/kafka_perf_report_*.xlsx`:

1. **Summary Sheet** - Start here for key findings and **maximum throughput** (MB/sec and msgs/sec)
2. **Producer Baseline** - See throughput/latency charts
3. **Recommendations** - Get actionable tuning suggestions

## 6. Customizing Tests

### 6.1 Modify Test Parameters

Edit `inventories/dev/group_vars/all/test_matrices.yml`:

```yaml
producer_test_matrix:
  quick:
    acks: ["1", "all"]         # Add acks=all
    batch_size: [16384, 64000] # Test larger batches
    linger_ms: [10, 20]        # Test higher linger
```

### 6.2 Run Specific Scenarios

```bash
# Only producer tests
ansible-playbook -i inventories/dev \
  ansible_collections/oso/test/playbooks/producer_baseline.yml

# Only message size analysis
ansible-playbook -i inventories/dev \
  ansible_collections/oso/test/playbooks/message_size_tests.yml
```

### 6.3 Create Custom Test Matrices

Use extra vars to override defaults:

```bash
ansible-playbook -i inventories/dev \
  ansible_collections/oso/test/playbooks/producer_baseline.yml \
  -e "test_profile=baseline" \
  -e "perf_num_records=5000000"
```

## 7. Next Steps

1. Review the [Configuration Reference](CONFIGURATION.md) for all options
2. Read [Test Scenarios](SCENARIOS.md) to understand each test type
3. Check [Troubleshooting](TROUBLESHOOTING.md) if you encounter issues
4. Explore the [Architecture](ARCHITECTURE.md) to understand the system

## Quick Reference

### Common Commands

```bash
# Quick producer test
ansible-playbook -i inventories/dev playbooks/producer_baseline.yml

# Full benchmark
ansible-playbook -i inventories/dev playbooks/full_benchmark.yml

# Dry run (check mode)
ansible-playbook -i inventories/dev playbooks/producer_baseline.yml --check

# Verbose output
ansible-playbook -i inventories/dev playbooks/producer_baseline.yml -v

# Only parse logs (skip tests)
ansible-playbook -i inventories/dev playbooks/full_benchmark.yml --tags parse,report
```

### Directory Reference

```
results/
├── raw_logs/      # Test output logs
├── parsed_data/   # JSON metrics
└── reports/       # Excel reports
```
