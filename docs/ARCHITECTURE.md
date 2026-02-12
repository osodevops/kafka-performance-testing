# Architecture Overview

This document explains how the Kafka Performance Testing system is designed and how its components work together.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│              (Ansible Playbooks / Command Line)                 │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Orchestration Layer                        │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ full_bench   │  │ producer_    │  │ consumer_    │         │
│  │ mark.yml     │  │ baseline.yml │  │ baseline.yml │  ...    │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Ansible Roles                            │
│                                                                 │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐  │
│  │  setup_    │ │   perf_    │ │   perf_    │ │  cleanup   │  │
│  │environment │ │  producer  │ │  consumer  │ │            │  │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘  │
│                                                                 │
│  ┌────────────┐ ┌────────────┐                                 │
│  │    log_    │ │   excel_   │                                 │
│  │   parser   │ │ generator  │                                 │
│  └────────────┘ └────────────┘                                 │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Execution Layer                            │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              Kafka CLI Tools                            │    │
│  │  kafka-producer-perf-test.sh  kafka-consumer-perf-test  │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              Python Scripts                             │    │
│  │  parse_perf_logs.py    generate_excel_report.py        │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Output Layer                              │
│                                                                 │
│  results/                                                       │
│  ├── raw_logs/       ← Test output logs                        │
│  ├── parsed_data/    ← JSON metrics                            │
│  └── reports/        ← Excel workbooks                         │
└─────────────────────────────────────────────────────────────────┘
```

## Component Descriptions

### Playbooks (Orchestration)

Playbooks define test scenarios and coordinate role execution.

| Playbook | Purpose |
|----------|---------|
| `full_benchmark.yml` | Master orchestrator - runs all scenarios |
| `producer_baseline.yml` | Producer configuration optimization |
| `consumer_baseline.yml` | Consumer configuration optimization |
| `load_scaling.yml` | Multi-client performance |
| `message_size_tests.yml` | Size vs. throughput analysis |
| `acks_tradeoff.yml` | Durability vs. performance |

### Ansible Roles

Each role has a specific responsibility:

#### setup_environment
- Creates results directories
- Verifies Kafka CLI tools
- Creates test topics
- Generates SSL client configuration

#### perf_producer
- Executes `kafka-producer-perf-test.sh`
- Supports async execution
- Captures output with metadata
- Saves structured log files

#### perf_consumer
- Executes `kafka-consumer-perf-test.sh`
- Creates consumer config files
- Handles consumer groups
- Captures throughput metrics

#### log_parser
- Invokes Python parser script
- Transforms raw logs to JSON
- Validates data integrity

#### excel_generator
- Invokes Python Excel script
- Creates 8-sheet workbook
- Generates charts and recommendations

#### cleanup
- Deletes test topics
- Archives logs (optional)
- Removes temporary files

### Python Scripts

#### parse_perf_logs.py
```
Input: results/raw_logs/*.log
Output: results/parsed_data/*.json

Flow:
1. Scan log directory
2. Identify log type (producer/consumer)
3. Extract configuration from headers
4. Parse metrics using regex
5. Output structured JSON
```

Regex patterns used:
```python
# Producer final line
r'(\d+) records sent, ([\d.]+) records/sec \(([\d.]+) MB/sec\), ...'

# Consumer CSV
r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}:\d{3}), ...'
```

#### generate_excel_report.py
```
Input: results/parsed_data/*.json
Output: results/reports/*.xlsx

Sheets:
1. Summary - Best configs, key metrics
2. Producer Baseline - Throughput/latency charts
3. Consumer Baseline - Consumer metrics
4. Load Scaling - Degradation analysis
5. Message Size - Size vs. performance
6. Acks Trade-offs - Durability analysis
7. Raw Data - Pivot table source
8. Recommendations - Optimization suggestions
```

## Data Flow

### Test Execution Flow

```
1. Playbook starts
   │
2. setup_environment role
   ├── Create directories
   ├── Verify Kafka tools
   └── Create test topic
   │
3. perf_producer role (repeated per config)
   ├── Build command with parameters
   ├── Execute async
   ├── Wait for completion
   └── Save log with metadata
   │
4. perf_consumer role (repeated per config)
   ├── Build consumer config
   ├── Execute test
   └── Save log
   │
5. log_parser role
   ├── Find all .log files
   ├── Parse each file
   └── Output combined JSON
   │
6. excel_generator role
   ├── Load JSON data
   ├── Create workbook
   ├── Add charts
   └── Save .xlsx
   │
7. cleanup role
   ├── Delete topic
   └── Archive logs (optional)
```

### Log Format

Producer log header:
```
# Producer Performance Test - baseline
# Test Run: 20241216T120000
# Configuration: acks=1, batch.size=16384, linger.ms=10, compression.type=zstd
# Record Size: 1024 bytes
# Num Records: 1000000
# Host: kafka-broker-1
# Date: 2024-12-16T12:00:00
```

Producer metrics line:
```
1000000 records sent, 14637.645096 records/sec (28.59 MB/sec),
3182.27 ms avg latency, 3613.00 ms max latency,
3289 ms 50th, 3467 ms 95th, 3568 ms 99th, 3603 ms 99.9th.
```

### JSON Structure

```json
{
  "test_type": "producer",
  "scenario": "baseline",
  "configuration": {
    "acks": "1",
    "batch_size": "16384",
    "linger_ms": "10",
    "compression_type": "zstd",
    "record_size": "1024"
  },
  "metrics": {
    "records_sent": 1000000,
    "throughput_rps": 14637.645,
    "throughput_mb": 28.59,
    "avg_latency_ms": 3182.27,
    "max_latency_ms": 3613.0,
    "p50_ms": 3289,
    "p95_ms": 3467,
    "p99_ms": 3568,
    "p999_ms": 3603
  },
  "filepath": "./logs/producer_baseline_acks_1.log",
  "parse_time": "2024-12-16T15:58:00"
}
```

## Configuration Hierarchy

```
1. Role defaults (lowest priority)
   └── roles/*/defaults/main.yml

2. Inventory group_vars
   └── examples/inventory/dev/group_vars/all/*.yml

3. Playbook vars
   └── vars: section in playbook

4. Extra vars (highest priority)
   └── -e "variable=value" on command line
```

## Parallel Execution

Producer tests use Ansible async for parallel execution:

```yaml
- name: Execute producer test
  shell: kafka-producer-perf-test.sh ...
  async: 80000   # Max runtime (ms)
  poll: 0        # Don't wait
  register: job

- name: Wait for completion
  async_status:
    jid: "{{ job.ansible_job_id }}"
  until: result.finished
  retries: 100
  delay: 10
```

## Extension Points

### Adding New Scenarios

1. Create new playbook in `playbooks/`
2. Define test matrix in `test_matrices.yml`
3. Import appropriate roles
4. Add scenario logic

### Adding New Metrics

1. Update regex in `parse_perf_logs.py`
2. Add fields to JSON output
3. Create new sheet in `generate_excel_report.py`
4. Update recommendations logic

### Custom Visualizations

The Excel generator uses openpyxl charts:
- `BarChart` for comparisons
- `LineChart` for trends
- `ScatterChart` for correlations

Add new charts in `create_*_sheet()` methods.
