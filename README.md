# Kafka Performance Testing Automation

Automated performance benchmarking for Apache Kafka with comprehensive Excel reporting and optimization recommendations.

## Features

- **5 Comprehensive Test Scenarios** - Producer baseline, consumer baseline, load scaling, message size impact, acknowledgment trade-offs
- **Automated Log Parsing** - Extracts metrics from kafka-producer-perf-test and kafka-consumer-perf-test output
- **Excel Reports with Charts** - 8-sheet workbook with visualizations and recommendations
- **Parametrized Testing** - Configurable test matrices for systematic parameter exploration
- **SSL/SASL Support** - Works with secured Kafka clusters
- **Parallel Execution** - Run multiple producers/consumers concurrently

## Quick Start

### Prerequisites

- Python 3.8+
- Ansible 2.10+
- Access to a Kafka cluster
- SSH access to test hosts (for remote execution)

### Installation

```bash
# Clone the repository
git clone https://github.com/osodevops/kafka-performance-testing.git
cd kafka-performance-testing

# Create virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configure Your Kafka Cluster

Edit the inventory file with your broker details:

```bash
vi inventories/dev/hosts.yml
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
ansible-playbook -i inventories/dev \
  ansible_collections/oso/test/playbooks/producer_baseline.yml

# Full benchmark suite
ansible-playbook -i inventories/dev \
  ansible_collections/oso/test/playbooks/full_benchmark.yml
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
| **Producer Baseline** | Optimize producer settings (acks, batch.size, linger.ms, compression) | `producer_baseline.yml` |
| **Consumer Baseline** | Optimize consumer settings (fetch.min.bytes, max.poll.records) | `consumer_baseline.yml` |
| **Load Scaling** | Measure performance with multiple producers/consumers | `load_scaling.yml` |
| **Message Size** | Analyze throughput vs. message size relationship | `message_size_tests.yml` |
| **Acks Trade-offs** | Quantify durability vs. performance impact | `acks_tradeoff.yml` |
| **Full Benchmark** | Run all scenarios with comprehensive report | `full_benchmark.yml` |

## Configuration

### Test Parameters

Edit `inventories/dev/group_vars/all/test_matrices.yml` to customize:

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
  ansible-playbook -i inventories/dev \
  ansible_collections/oso/test/playbooks/producer_baseline.yml
```

## Legacy Commands

The following original collection commands are still available:

```bash
# Basic connectivity test
ansible-playbook -i inventories/local oso.test.produce_consume

# Simple performance test (original)
ansible-playbook -i inventories/local oso.test.simple
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

## Project Structure

```
kafka-performance-testing/
├── ansible_collections/oso/test/
│   ├── playbooks/           # Test scenario playbooks
│   │   ├── full_benchmark.yml
│   │   ├── producer_baseline.yml
│   │   ├── consumer_baseline.yml
│   │   └── ...
│   └── roles/               # Ansible roles
│       ├── setup_environment/
│       ├── perf_producer/
│       ├── perf_consumer/
│       ├── log_parser/
│       ├── excel_generator/
│       └── cleanup/
├── scripts/                 # Python utilities
│   ├── parse_perf_logs.py
│   ├── generate_excel_report.py
│   └── aggregate_results.py
├── inventories/             # Ansible inventories
│   ├── dev/
│   └── local/
├── results/                 # Test outputs (gitignored)
├── requirements.txt         # Python dependencies
└── Dockerfile              # Container build
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

Apache 2.0

## Support

- [GitHub Issues](https://github.com/osodevops/kafka-performance-testing/issues)
- [OSO DevOps](https://osodevops.io)
