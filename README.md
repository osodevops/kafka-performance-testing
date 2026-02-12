# Kafka Performance Testing Automation

[![Ansible Galaxy](https://img.shields.io/badge/galaxy-osodevops.kafka__perf__testing-blue.svg)](https://galaxy.ansible.com/ui/repo/published/osodevops/kafka_perf_testing/)
[![CI](https://github.com/osodevops/kafka-performance-testing/actions/workflows/ci.yml/badge.svg)](https://github.com/osodevops/kafka-performance-testing/actions/workflows/ci.yml)

Automated performance benchmarking for Apache Kafka with comprehensive Excel reporting and optimization recommendations.

## Features

- **5 Comprehensive Test Scenarios** - Producer baseline, consumer baseline, load scaling, message size impact, acknowledgment trade-offs
- **Automated Log Parsing** - Extracts metrics from kafka-producer-perf-test and kafka-consumer-perf-test output
- **Excel Reports with Charts** - 10-sheet workbook with 30+ visualizations and recommendations
- **Parametrized Testing** - Configurable test matrices for systematic parameter exploration
- **SSL/SASL Support** - Works with secured Kafka clusters
- **Parallel Execution** - Run multiple producers/consumers concurrently

## Installation

### From Ansible Galaxy

```bash
ansible-galaxy collection install osodevops.kafka_perf_testing
```

### From Source

```bash
git clone https://github.com/osodevops/kafka-performance-testing.git
cd kafka-performance-testing

# Create virtual environment and install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Python Requirements

The log parsing and Excel report generation scripts require:

- `openpyxl >= 3.1.0`
- `pandas >= 2.0.0`
- `numpy >= 1.24.0`

### Prerequisites

- Python 3.8+
- Ansible 2.15+
- Access to a Kafka cluster
- SSH access to test hosts (for remote execution)

## Quick Start

### Configure Your Kafka Cluster

Copy the example inventory and edit with your broker details:

```bash
cp -r examples/inventory/dev inventories/myenv
vi inventories/myenv/hosts.yml
```

```yaml
all:
  hosts:
    kafka-broker-1:
      ansible_host: broker1.example.com
      broker_id: 0
    kafka-broker-2:
      ansible_host: broker2.example.com
      broker_id: 1
    kafka-broker-3:
      ansible_host: broker3.example.com
      broker_id: 2
  vars:
    kafka_broker:
      hosts:
        - broker1.example.com:9092
        - broker2.example.com:9092
        - broker3.example.com:9092
```

### Run Your First Test

```bash
# Quick producer baseline test
ansible-playbook -i inventories/myenv playbooks/producer_baseline.yml

# Full benchmark suite
ansible-playbook -i inventories/myenv playbooks/full_benchmark.yml
```

### View Results

```bash
# Results are saved in the results/ directory
ls results/reports/

# Open the Excel report
open results/reports/kafka_perf_report_*.xlsx
```

## Test Scenarios

| Scenario | Purpose | Playbook |
|----------|---------|----------|
| **Producer Baseline** | Optimize producer settings (acks, batch.size, linger.ms, compression) | `playbooks/producer_baseline.yml` |
| **Consumer Baseline** | Optimize consumer settings (fetch.min.bytes, max.poll.records) | `playbooks/consumer_baseline.yml` |
| **Load Scaling** | Measure performance with multiple producers/consumers | `playbooks/load_scaling.yml` |
| **Message Size** | Analyze throughput vs. message size relationship | `playbooks/message_size_tests.yml` |
| **Acks Trade-offs** | Quantify durability vs. performance impact | `playbooks/acks_tradeoff.yml` |
| **Full Benchmark** | Run all scenarios with comprehensive report | `playbooks/full_benchmark.yml` |

## Configuration

### Test Parameters

Edit `inventories/<env>/group_vars/all/test_matrices.yml` to customize:

```yaml
producer_test_matrix:
  quick:
    acks: ["1"]
    batch_size: [16384, 32768]
    linger_ms: [10]
    compression_type: ["zstd"]
    record_size: [1024]
```

### Key Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `perf_num_records` | 1000000 | Number of records per test |
| `perf_record_size` | 1024 | Message size in bytes |
| `perf_throughput` | -1 | Target throughput (-1 = unlimited) |
| `ssl_enabled` | false | Enable SSL/SASL authentication |
| `test_profile` | quick | Test profile (quick or baseline) |

## Output Structure

```
results/
├── raw_logs/          # Raw kafka-*-perf-test output
│   ├── producer_baseline_acks1_batch16384_*.log
│   └── consumer_baseline_fetch10240_*.log
├── parsed_data/       # JSON parsed metrics
│   └── parsed_results_20241216_120000.json
└── reports/           # Excel reports with charts
    └── kafka_perf_report_20241216_120000.xlsx
```

## Excel Report Sheets

The generated report contains 10 sheets with 30+ charts:

1. **Dashboard** - Executive summary with KPIs and 4 key visualization charts
2. **Throughput Analysis** - Deep dive into throughput with 4 charts (by acks, batch size, compression)
3. **Latency Analysis** - Latency percentiles, distributions, and 4 analysis charts
4. **Trade-off Analysis** - THE KNEE CHART showing latency vs throughput saturation curve
5. **Scaling Performance** - Producer scaling degradation analysis with 4 charts
6. **Configuration Heatmap** - Multi-dimensional parameter heatmaps
7. **Message Size Impact** - Size efficiency curves and analysis
8. **Acks Comparison** - Durability vs performance trade-off visualization
9. **Raw Data** - Complete data for custom pivot tables
10. **Recommendations** - Scored configurations by use case (throughput, balanced, durability)

See [Understanding Results](docs/UNDERSTANDING_RESULTS.md) for detailed explanation of all metrics and charts.

## Using Docker

```bash
# Build the container
docker build -t kafka-perf-testing .

# Run tests
docker run -v $(pwd)/results:/app/results \
  -v $(pwd)/inventories:/app/inventories \
  kafka-perf-testing \
  ansible-playbook -i inventories/myenv playbooks/producer_baseline.yml
```

## Project Structure

```
kafka-performance-testing/
├── galaxy.yml               # Ansible Galaxy collection metadata
├── playbooks/               # Test scenario playbooks
│   ├── full_benchmark.yml
│   ├── producer_baseline.yml
│   ├── consumer_baseline.yml
│   └── ...
├── roles/                   # Ansible roles
│   ├── setup_environment/
│   ├── perf_producer/
│   ├── perf_consumer/
│   ├── log_parser/
│   ├── excel_generator/
│   └── cleanup/
├── scripts/                 # Python utilities
│   ├── parse_perf_logs.py
│   ├── generate_excel_report.py
│   └── aggregate_results.py
├── meta/                    # Collection metadata
│   └── runtime.yml
├── examples/                # Example inventories
│   └── inventory/
│       ├── dev/
│       └── local/
├── docs/                    # Documentation
├── results/                 # Test outputs (gitignored)
├── requirements.txt         # Python dependencies
├── requirements.yml         # Galaxy collection dependencies
└── Dockerfile               # Container build
```

## Documentation

- [Getting Started Guide](docs/GETTING_STARTED.md) - Detailed setup instructions
- [Running Tests](docs/RUNNING_TESTS.md) - Step-by-step guide to running all test scenarios
- [Understanding Results](docs/UNDERSTANDING_RESULTS.md) - Complete guide to metrics, charts, and recommendations
- [Offline Installation](docs/OFFLINE_INSTALLATION.md) - Air-gapped environment setup
- [Configuration Reference](docs/CONFIGURATION.md) - All variables and options
- [Architecture Overview](docs/ARCHITECTURE.md) - How the system works
- [Test Scenarios](docs/SCENARIOS.md) - Detailed scenario descriptions
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `make lint` to validate
5. Submit a pull request

## License

Apache 2.0

## Support

- [GitHub Issues](https://github.com/osodevops/kafka-performance-testing/issues)
- [OSO DevOps](https://osodevops.io)
