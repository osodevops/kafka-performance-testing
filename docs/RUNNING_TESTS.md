# Running Kafka Performance Tests - Step-by-Step Guide

This guide provides complete instructions for running performance tests, from environment setup to analyzing results.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (Local Docker)](#quick-start-local-docker)
3. [Running Against a Remote Cluster](#running-against-a-remote-cluster)
4. [Test Scenarios](#test-scenarios)
5. [Customizing Tests](#customizing-tests)
6. [Generating Reports](#generating-reports)
7. [Common Workflows](#common-workflows)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.8+ | Script execution, report generation |
| Docker & Docker Compose | Latest | Local Kafka cluster |
| Ansible | 2.10+ | Test orchestration |
| Git | Any | Clone repository |

### Verify Installation

```bash
# Check all prerequisites
python3 --version    # Should be 3.8+
docker --version     # Should be 20.10+
docker-compose --version
ansible --version    # Should be 2.10+
```

---

## Quick Start (Local Docker)

The fastest way to run tests is using the included Docker Compose setup.

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/osodevops/kafka-performance-testing.git
cd kafka-performance-testing

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Start the Kafka Cluster

```bash
# Start 3-broker Kafka cluster + Zookeeper + Kafka UI
docker-compose up -d

# Wait for services to be healthy (takes ~60 seconds)
docker-compose ps

# Expected output - all services should show "healthy" or "running"
# NAME              STATUS
# kafka-broker-1    healthy
# kafka-broker-2    healthy
# kafka-broker-3    healthy
# kafka-perf-test   running
# kafka-ui          running
# zookeeper         healthy
```

### Step 3: Verify Cluster Health

```bash
# Open Kafka UI in browser
open http://localhost:8080

# Or verify via command line
docker exec kafka-broker-1 kafka-broker-api-versions --bootstrap-server localhost:29092
```

### Step 4: Run Your First Test

```bash
# Enter the test container
docker exec -it kafka-perf-test bash

# Inside the container, run a quick producer baseline test
ansible-playbook -i examples/inventory/local \
  playbooks/producer_baseline.yml

# This will:
# 1. Create test topics
# 2. Run producer performance tests
# 3. Parse the results
# 4. Generate an Excel report
```

### Step 5: View Results

```bash
# Exit the container (Ctrl+D or type 'exit')

# Results are mounted to your host machine
ls results/reports/

# Open the Excel report
open results/reports/kafka_perf_report_*.xlsx

# Or view raw logs
cat results/raw_logs/*.log
```

### Step 6: Cleanup

```bash
# Stop the cluster (preserves data)
docker-compose down

# Stop and remove all data (clean slate)
docker-compose down -v
```

---

## Running Against a Remote Cluster

For testing production or staging Kafka clusters.

### Step 1: Configure Inventory

Create or edit `examples/inventory/dev/hosts.yml`:

```yaml
all:
  hosts:
    # Define your Kafka broker hosts
    kafka-broker-1:
      ansible_host: broker1.example.com
      ansible_user: ec2-user
      ansible_ssh_private_key_file: ~/.ssh/my-key.pem
      broker_id: 0
    kafka-broker-2:
      ansible_host: broker2.example.com
      ansible_user: ec2-user
      ansible_ssh_private_key_file: ~/.ssh/my-key.pem
      broker_id: 1
    kafka-broker-3:
      ansible_host: broker3.example.com
      ansible_user: ec2-user
      ansible_ssh_private_key_file: ~/.ssh/my-key.pem
      broker_id: 2

  vars:
    # Kafka connection settings
    kafka_broker:
      hosts:
        - broker1.example.com:9092
        - broker2.example.com:9092
        - broker3.example.com:9092

    # Results directory
    results_base_dir: "./results"
```

### Step 2: Configure Authentication (If Required)

For SSL/SASL clusters, edit `examples/inventory/dev/group_vars/all/security.yml`:

```yaml
# SSL Configuration
ssl_enabled: true
ssl_truststore_location: /path/to/truststore.jks
ssl_truststore_password: "your-password"

# SASL Configuration (if using)
sasl_enabled: true
sasl_mechanism: PLAIN  # or SCRAM-SHA-256, SCRAM-SHA-512
sasl_username: "your-username"
sasl_password: "your-password"
```

### Step 3: Verify Connectivity

```bash
# Test SSH connectivity
ansible -i examples/inventory/dev all -m ping

# Test Kafka connectivity with a simple produce/consume
ansible-playbook -i examples/inventory/dev \
  playbooks/produce_consume.yml
```

### Step 4: Run Tests

```bash
# Run producer baseline tests
ansible-playbook -i examples/inventory/dev \
  playbooks/producer_baseline.yml

# Or run the full benchmark suite
ansible-playbook -i examples/inventory/dev \
  playbooks/full_benchmark.yml
```

---

## Test Scenarios

### Available Test Playbooks

| Playbook | Description | Duration (Quick) | Duration (Baseline) |
|----------|-------------|------------------|---------------------|
| `producer_baseline.yml` | Producer config optimization | ~5 min | ~30 min |
| `consumer_baseline.yml` | Consumer config optimization | ~5 min | ~20 min |
| `load_scaling.yml` | Multi-producer/consumer scaling | ~10 min | ~45 min |
| `message_size_tests.yml` | Message size impact analysis | ~5 min | ~20 min |
| `acks_tradeoff.yml` | Durability vs performance | ~5 min | ~15 min |
| `full_benchmark.yml` | All scenarios combined | ~30 min | ~2+ hours |

### Running Individual Scenarios

```bash
# Producer Baseline - Test different producer configurations
ansible-playbook -i examples/inventory/local \
  playbooks/producer_baseline.yml

# Consumer Baseline - Test different consumer configurations
ansible-playbook -i examples/inventory/local \
  playbooks/consumer_baseline.yml

# Load Scaling - Test with multiple producers/consumers
ansible-playbook -i examples/inventory/local \
  playbooks/load_scaling.yml

# Message Size - Test different message sizes
ansible-playbook -i examples/inventory/local \
  playbooks/message_size_tests.yml

# Acks Trade-off - Compare acks=0, acks=1, acks=all
ansible-playbook -i examples/inventory/local \
  playbooks/acks_tradeoff.yml
```

### Running the Full Benchmark

```bash
# Full benchmark with quick profile (faster, fewer combinations)
ansible-playbook -i examples/inventory/local \
  playbooks/full_benchmark.yml \
  -e "test_profile=quick"

# Full benchmark with baseline profile (comprehensive)
ansible-playbook -i examples/inventory/local \
  playbooks/full_benchmark.yml \
  -e "test_profile=baseline"

# Run only specific scenarios
ansible-playbook -i examples/inventory/local \
  playbooks/full_benchmark.yml \
  -e "run_producer_baseline=true" \
  -e "run_consumer_baseline=false" \
  -e "run_load_scaling=false" \
  -e "run_message_size=true" \
  -e "run_acks_tradeoff=true"
```

### Using Ansible Tags

```bash
# Run only producer tests
ansible-playbook -i examples/inventory/local \
  playbooks/full_benchmark.yml \
  --tags producer

# Run only report generation (skip tests)
ansible-playbook -i examples/inventory/local \
  playbooks/full_benchmark.yml \
  --tags report

# Run tests but skip report
ansible-playbook -i examples/inventory/local \
  playbooks/full_benchmark.yml \
  --skip-tags report
```

---

## Customizing Tests

### Test Profiles

Two built-in profiles are available:

**Quick Profile** (default):
- Reduced parameter combinations
- Faster execution (~5-10 min per scenario)
- Good for development and quick checks

**Baseline Profile**:
- Comprehensive parameter sweep
- Longer execution (~30+ min per scenario)
- Recommended for production benchmarking

```bash
# Use quick profile (default)
ansible-playbook -i examples/inventory/local \
  playbooks/producer_baseline.yml \
  -e "test_profile=quick"

# Use baseline profile
ansible-playbook -i examples/inventory/local \
  playbooks/producer_baseline.yml \
  -e "test_profile=baseline"
```

### Modifying Test Parameters

Edit `examples/inventory/dev/group_vars/all/test_matrices.yml`:

```yaml
# Producer test configurations
producer_test_matrix:
  quick:
    acks:
      - "1"
      - "all"              # Add acks=all to quick tests
    batch_size:
      - 16384
      - 32768
      - 65536              # Add larger batch size
    linger_ms:
      - 10
      - 20                 # Add higher linger
    compression_type:
      - "zstd"
    record_size:
      - 1024
      - 4096               # Add larger message size

# Adjust default test parameters
perf_defaults:
  num_records: 2000000     # Increase from 1M to 2M
  throughput: -1           # -1 = unlimited
  topic_partitions: 24     # Increase partitions
```

### Override Parameters at Runtime

```bash
# Override number of records
ansible-playbook -i examples/inventory/local \
  playbooks/producer_baseline.yml \
  -e "perf_num_records=5000000"

# Override multiple parameters
ansible-playbook -i examples/inventory/local \
  playbooks/producer_baseline.yml \
  -e "perf_num_records=2000000" \
  -e "perf_record_size=2048" \
  -e "test_profile=baseline"
```

---

## Generating Reports

### Automatic Report Generation

Reports are generated automatically after tests complete. The Excel report is saved to:

```
results/reports/kafka_perf_report_YYYYMMDD_HHMMSS.xlsx
```

### Manual Report Generation

If you need to regenerate reports from existing data:

```bash
# Activate virtual environment
source venv/bin/activate

# Generate report from parsed JSON data
python scripts/generate_excel_report.py \
  ./results/parsed_data/parsed_results_*.json \
  ./results/reports/my_report.xlsx \
  --verbose
```

### Re-parse Logs and Generate Report

```bash
# Parse logs manually
python scripts/parse_perf_logs.py \
  ./results/raw_logs/ \
  ./results/parsed_data/parsed_results.json

# Then generate report
python scripts/generate_excel_report.py \
  ./results/parsed_data/parsed_results.json \
  ./results/reports/kafka_perf_report.xlsx
```

### Report Contents

The generated Excel report contains 10 sheets:

1. **Dashboard** - Executive summary with KPIs and 4 charts
2. **Throughput Analysis** - Throughput deep dive with 4 charts
3. **Latency Analysis** - Latency percentiles and distributions
4. **Trade-off Analysis** - The critical "knee chart"
5. **Scaling Performance** - Multi-producer scaling analysis
6. **Configuration Heatmap** - Parameter combination heatmaps
7. **Message Size Impact** - Size vs performance analysis
8. **Acks Comparison** - Durability vs performance trade-offs
9. **Raw Data** - Complete data for pivot tables
10. **Recommendations** - Scored configurations by use case

---

## Common Workflows

### Workflow 1: Quick Sanity Check

Run a fast test to verify Kafka cluster health:

```bash
# Start cluster (if local)
docker-compose up -d

# Enter container
docker exec -it kafka-perf-test bash

# Run minimal test
ansible-playbook -i examples/inventory/local \
  playbooks/producer_baseline.yml \
  -e "test_profile=quick" \
  -e "perf_num_records=100000"

# Check results
cat results/raw_logs/*.log | tail -20
```

### Workflow 2: Production Baseline

Comprehensive testing for production cluster:

```bash
# Run full baseline (2+ hours)
ansible-playbook -i examples/inventory/dev \
  playbooks/full_benchmark.yml \
  -e "test_profile=baseline"

# View detailed report
open results/reports/kafka_full_benchmark_*.xlsx
```

### Workflow 3: Compare Before/After Change

Test cluster before and after a configuration change:

```bash
# Run baseline tests BEFORE change
ansible-playbook -i examples/inventory/dev \
  playbooks/producer_baseline.yml

# Rename results
mv results/reports/kafka_perf_report_*.xlsx results/reports/BEFORE_change.xlsx

# Make your Kafka configuration changes...

# Run baseline tests AFTER change
ansible-playbook -i examples/inventory/dev \
  playbooks/producer_baseline.yml

# Rename results
mv results/reports/kafka_perf_report_*.xlsx results/reports/AFTER_change.xlsx

# Compare the two reports
```

### Workflow 4: Focus on Specific Parameters

Test specific configuration combinations:

```bash
# Test only acks settings
ansible-playbook -i examples/inventory/dev \
  playbooks/acks_tradeoff.yml

# Test only message sizes
ansible-playbook -i examples/inventory/dev \
  playbooks/message_size_tests.yml

# Test producer scaling only
ansible-playbook -i examples/inventory/dev \
  playbooks/load_scaling.yml
```

### Workflow 5: Iterative Optimization

Find optimal configuration through iteration:

```bash
# Step 1: Run quick baseline
ansible-playbook -i examples/inventory/local \
  playbooks/full_benchmark.yml \
  -e "test_profile=quick"

# Step 2: Review recommendations sheet
# Identify top 3 configurations

# Step 3: Update test_matrices.yml with narrower ranges
# Focus on promising parameter values

# Step 4: Run targeted tests
ansible-playbook -i examples/inventory/local \
  playbooks/producer_baseline.yml \
  -e "test_profile=baseline"

# Step 5: Repeat until optimal configuration found
```

---

## Troubleshooting

### Common Issues

#### Tests Fail to Start

```bash
# Check Kafka is accessible
docker exec kafka-broker-1 kafka-topics --bootstrap-server localhost:29092 --list

# Check test container can reach Kafka
docker exec kafka-perf-test nc -zv kafka-broker-1 29092
```

#### Permission Denied Errors

```bash
# Fix results directory permissions
chmod -R 755 results/
chown -R $(whoami) results/
```

#### Report Generation Fails

```bash
# Verify Python environment
source venv/bin/activate
pip install -r requirements.txt

# Check parsed data exists
ls -la results/parsed_data/

# Run with verbose flag
python scripts/generate_excel_report.py \
  ./results/parsed_data/*.json \
  ./results/reports/test.xlsx \
  --verbose
```

#### Slow Test Performance

```bash
# Reduce number of records for faster tests
ansible-playbook -i examples/inventory/local \
  playbooks/producer_baseline.yml \
  -e "perf_num_records=500000"

# Use quick profile
ansible-playbook -i examples/inventory/local \
  playbooks/full_benchmark.yml \
  -e "test_profile=quick"
```

#### Docker Compose Issues

```bash
# Rebuild containers
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d

# Check container logs
docker-compose logs kafka-broker-1
docker-compose logs kafka-perf-test
```

### Getting Help

```bash
# View playbook options
ansible-playbook --help

# Dry run (check mode)
ansible-playbook -i examples/inventory/local \
  playbooks/producer_baseline.yml \
  --check

# Verbose output
ansible-playbook -i examples/inventory/local \
  playbooks/producer_baseline.yml \
  -vvv
```

---

## Quick Reference

### Essential Commands

```bash
# Start local Kafka cluster
docker-compose up -d

# Enter test container
docker exec -it kafka-perf-test bash

# Run quick producer test
ansible-playbook -i examples/inventory/local \
  playbooks/producer_baseline.yml

# Run full benchmark
ansible-playbook -i examples/inventory/local \
  playbooks/full_benchmark.yml

# View results
open results/reports/kafka_perf_report_*.xlsx

# Stop cluster
docker-compose down
```

### Directory Structure

```
kafka-performance-testing/
├── playbooks/                                # Test playbooks
├── examples/inventory/
│   ├── local/                               # Local Docker inventory
│   └── dev/                                 # Remote cluster inventory
├── results/
│   ├── raw_logs/                            # Raw test output
│   ├── parsed_data/                         # Parsed JSON metrics
│   └── reports/                             # Excel reports
├── scripts/                                 # Python utilities
├── docker-compose.yml                       # Local Kafka cluster
└── requirements.txt                         # Python dependencies
```

### Test Duration Estimates

| Test | Quick Profile | Baseline Profile |
|------|---------------|------------------|
| Producer Baseline | 5 min | 30 min |
| Consumer Baseline | 5 min | 20 min |
| Load Scaling | 10 min | 45 min |
| Message Size | 5 min | 20 min |
| Acks Trade-off | 5 min | 15 min |
| **Full Benchmark** | **30 min** | **2+ hours** |
