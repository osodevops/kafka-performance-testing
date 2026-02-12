# Test Scenarios

Detailed documentation for each test scenario defined in the PRD.

## Overview

| Scenario | Purpose | Key Variables | Metrics |
|----------|---------|---------------|---------|
| Producer Baseline | Optimize producer config | acks, batch.size, linger.ms, compression | Throughput, latency |
| Consumer Baseline | Optimize consumer config | fetch.min.bytes, max.poll.records | Throughput, rebalance time |
| Load Scaling | Multi-client impact | num_producers, num_consumers | Degradation curves |
| Message Size | Size vs. performance | record.size | MB/sec efficiency |
| Acks Trade-off | Durability vs. speed | acks, replication_factor | Trade-off analysis |

---

## Scenario 1: Producer Configuration Baseline

### Purpose
Identify optimal producer settings for maximum throughput and/or minimum latency.

### Variables Tested

| Variable | Values | Impact |
|----------|--------|--------|
| `acks` | 0, 1, all | Durability vs. speed |
| `batch.size` | 1KB - 64KB | Batching efficiency |
| `linger.ms` | 0 - 50ms | Wait time for batching |
| `compression.type` | none, snappy, lz4, zstd | Network vs. CPU trade-off |
| `record.size` | 512B - 4KB | Message payload |

### Metrics Captured

- **Records/sec**: Raw throughput
- **MB/sec**: Data throughput
- **Avg latency (ms)**: Average produce time
- **Max latency (ms)**: Worst case
- **Percentiles**: P50, P95, P99, P99.9

### Running

```bash
# Quick profile (subset of configs)
ansible-playbook -i examples/inventory/dev playbooks/producer_baseline.yml

# Full baseline (all combinations)
ansible-playbook -i examples/inventory/dev playbooks/producer_baseline.yml \
  -e "test_profile=baseline"

# Custom configuration
ansible-playbook -i examples/inventory/dev playbooks/producer_baseline.yml \
  -e '{"test_acks": ["1", "all"], "test_batch_sizes": [16384, 32768]}'
```

### Expected Results

- Higher `batch.size` + `linger.ms` = Better throughput, higher latency
- Compression = Better throughput (less network), slight CPU overhead
- `acks=0` = Fastest, no durability guarantee
- `acks=all` = Slowest, strongest durability

---

## Scenario 2: Consumer Configuration Baseline

### Purpose
Identify optimal consumer settings for maximum consumption throughput.

### Variables Tested

| Variable | Values | Impact |
|----------|--------|--------|
| `fetch.min.bytes` | 1KB - 100KB | Min data before returning |
| `fetch.max.wait.ms` | 0 - 500ms | Max wait for min bytes |
| `max.poll.records` | 100 - 5000 | Records per poll |
| `receive.buffer.bytes` | 1MB - 8MB | TCP receive buffer |

### Metrics Captured

- **MB/sec**: Consumption throughput
- **Records/sec**: Message throughput
- **Rebalance time (ms)**: Time to rebalance
- **Fetch time (ms)**: Time fetching data

### Running

```bash
# Quick profile
ansible-playbook -i examples/inventory/dev playbooks/consumer_baseline.yml

# Full baseline
ansible-playbook -i examples/inventory/dev playbooks/consumer_baseline.yml \
  -e "test_profile=baseline"
```

### Expected Results

- Higher `fetch.min.bytes` = Better throughput (larger batches)
- Higher `max.poll.records` = Better throughput if processing is fast
- Too high values may cause timeouts or memory issues

---

## Scenario 3: Load Scaling

### Purpose
Measure performance degradation with multiple concurrent producers/consumers.

### Variables Tested

| Variable | Values | Impact |
|----------|--------|--------|
| `num_producers` | 1, 3, 5, 10 | Producer concurrency |
| `num_consumers` | 1, 3, 5 | Consumer concurrency |

### Metrics Captured

- **Per-client throughput**: Individual performance
- **Aggregate throughput**: Total cluster throughput
- **Throughput degradation**: Percentage drop vs. single client
- **Latency impact**: Increased latency under load

### Running

```bash
# Default scaling test
ansible-playbook -i examples/inventory/dev playbooks/load_scaling.yml

# Custom producer count
ansible-playbook -i examples/inventory/dev playbooks/load_scaling.yml \
  -e '{"scaling_num_producers": [1, 5, 10, 20]}'
```

### Expected Results

- Linear scaling up to broker capacity
- Degradation starts when brokers saturate
- Network becomes bottleneck before CPU typically
- Consumer scaling limited by partition count

---

## Scenario 4: Message Size Impact

### Purpose
Understand the relationship between message size and performance.

### Variables Tested

| Variable | Values | Impact |
|----------|--------|--------|
| `record.size` | 128B - 16KB | Message payload |
| `compression.type` | none, zstd | Compression effect |

### Fixed Settings

- `acks`: 1 (balanced durability)
- `linger.ms`: 10
- `batch.size`: Auto-scaled (10x record size)

### Metrics Captured

- **Throughput (MB/sec)**: Raw data rate
- **Throughput (records/sec)**: Message rate
- **Latency**: Impact on produce time
- **Compression ratio**: Space savings (with zstd)

### Running

```bash
# Default message sizes
ansible-playbook -i examples/inventory/dev playbooks/message_size_tests.yml

# Custom sizes
ansible-playbook -i examples/inventory/dev playbooks/message_size_tests.yml \
  -e '{"test_record_sizes": [256, 1024, 4096, 16384, 65536]}'
```

### Expected Results

- Small messages: Lower MB/sec, higher records/sec
- Large messages: Higher MB/sec, lower records/sec
- Optimal size depends on use case (event streaming vs. batch data)
- Compression benefits increase with message size

---

## Scenario 5: Acknowledgment Trade-offs

### Purpose
Quantify the durability vs. performance trade-off of different acks settings.

### Variables Tested

| Variable | Values | Impact |
|----------|--------|--------|
| `acks` | 0, 1, all | Durability level |
| `replication_factor` | 1, 3 | Replica count |

### Acks Settings Explained

| Setting | Behavior | Durability | Performance |
|---------|----------|------------|-------------|
| `acks=0` | Fire and forget | None | Fastest |
| `acks=1` | Leader only | Medium | Balanced |
| `acks=all` | All in-sync replicas | Strongest | Slowest |

### Metrics Captured

- **Throughput comparison**: Performance difference
- **Latency breakdown**: Per-ack latency impact
- **Percentage difference**: `acks=0` vs `acks=all`

### Running

```bash
# Default acks test
ansible-playbook -i examples/inventory/dev playbooks/acks_tradeoff.yml

# Specific acks values
ansible-playbook -i examples/inventory/dev playbooks/acks_tradeoff.yml \
  -e '{"test_acks": ["1", "all"]}'
```

### Expected Results

- `acks=0` typically 10-50% faster than `acks=all`
- Impact varies with network latency and replica count
- Higher replication factor increases `acks=all` latency

### Recommendations

| Use Case | Recommended acks |
|----------|------------------|
| Metrics/logs (lossy OK) | 0 or 1 |
| Event streaming | 1 |
| Financial transactions | all |
| Audit logs | all |

---

## Full Benchmark

### Purpose
Run all scenarios and generate comprehensive report.

### Running

```bash
# Full benchmark with all scenarios
ansible-playbook -i examples/inventory/dev playbooks/full_benchmark.yml

# Selective scenarios
ansible-playbook -i examples/inventory/dev playbooks/full_benchmark.yml \
  -e "run_producer_baseline=true" \
  -e "run_consumer_baseline=true" \
  -e "run_load_scaling=false" \
  -e "run_message_size=false" \
  -e "run_acks_tradeoff=false"

# Using tags
ansible-playbook -i examples/inventory/dev playbooks/full_benchmark.yml \
  --tags "producer,consumer"
```

### Output

Complete Excel report with:
- Summary of all scenarios
- Best configurations identified
- Trade-off analysis
- Actionable recommendations

---

## Custom Scenarios

### Creating a New Scenario

1. Create playbook:
```yaml
# playbooks/my_scenario.yml
- name: My Custom Scenario
  hosts: all
  vars:
    scenario_name: "my_scenario"
  tasks:
    - include_role:
        name: setup_environment
    - include_role:
        name: perf_producer
      vars:
        # Your configuration
    - include_role:
        name: log_parser
    - include_role:
        name: excel_generator
```

2. Add to test_matrices.yml:
```yaml
my_scenario_matrix:
  param1: [value1, value2]
  param2: [value3, value4]
```

3. Run:
```bash
ansible-playbook -i examples/inventory/dev playbooks/my_scenario.yml
```
