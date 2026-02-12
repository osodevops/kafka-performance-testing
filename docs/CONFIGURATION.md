# Configuration Reference

Complete reference for all configuration variables and options.

## Inventory Configuration

### Host Variables

Define in `examples/inventory/dev/hosts.yml`:

```yaml
all:
  hosts:
    kafka-broker-1:
      ansible_host: broker1.example.com   # Broker hostname
      broker_id: 0                        # Kafka broker ID
```

### Group Variables

Define in `examples/inventory/dev/group_vars/all/`:

#### Connection Settings (`default.yml`)

| Variable | Default | Description |
|----------|---------|-------------|
| `ansible_user` | `ansible` | SSH username |
| `ansible_connection` | `ssh` | Connection type |
| `ansible_become` | `true` | Use privilege escalation |
| `kafka_broker_cluster_name` | - | Cluster identifier |

#### Test Matrices (`test_matrices.yml`)

See below for complete matrix configuration.

## Test Configuration

### Producer Test Matrix

```yaml
producer_test_matrix:
  baseline:
    acks:
      - "0"           # Fire-and-forget
      - "1"           # Leader acknowledgment
      - "all"         # All replicas
    batch_size:
      - 1024          # 1 KB
      - 8192          # 8 KB
      - 16384         # 16 KB (default)
      - 32768         # 32 KB
      - 64000         # 64 KB
    linger_ms:
      - 0             # No wait
      - 5
      - 10            # Default
      - 20
      - 50
    compression_type:
      - "none"
      - "snappy"
      - "lz4"
      - "zstd"        # Best ratio/speed
    record_size:
      - 512
      - 1024          # 1 KB (default)
      - 2048
      - 4096
  quick:
    # Reduced set for faster testing
    acks: ["1"]
    batch_size: [16384, 32768]
    linger_ms: [10]
    compression_type: ["zstd"]
    record_size: [1024]
```

### Consumer Test Matrix

```yaml
consumer_test_matrix:
  baseline:
    fetch_min_bytes:
      - 1024          # 1 KB
      - 10240         # 10 KB
      - 102400        # 100 KB
    fetch_max_wait_ms:
      - 0             # No wait
      - 50
      - 100           # Default
      - 500
    max_poll_records:
      - 100
      - 500           # Default
      - 1000
      - 5000
    receive_buffer_bytes:
      - 1048576       # 1 MB
      - 8388608       # 8 MB
```

### Scaling Test Matrix

```yaml
scaling_test_matrix:
  num_producers:
    - 1
    - 3
    - 5
    - 10
  num_consumers:
    - 1
    - 3
    - 5
```

### Message Size Matrix

```yaml
message_size_matrix:
  record_size:
    - 128
    - 256
    - 512
    - 1024
    - 2048
    - 4096
    - 8192
    - 16384
  compression_type:
    - "none"
    - "zstd"
  acks: "1"
  linger_ms: 10
  batch_size_multiplier: 10
```

### Acks Trade-off Matrix

```yaml
acks_tradeoff_matrix:
  acks:
    - "0"
    - "1"
    - "all"
  replication_factor:
    - 1
    - 3
  batch_size: 16384
  linger_ms: 10
  record_size: 1024
```

## Role Variables

### setup_environment Role

| Variable | Default | Description |
|----------|---------|-------------|
| `kafka_home` | `/usr/local` | Kafka installation directory |
| `binary_base_path` | `{{ kafka_home }}` | Path to Kafka binaries |
| `perf_topic_name` | `perf-test` | Test topic name |
| `perf_topic_partitions` | `12` | Number of partitions |
| `perf_replication_factor` | `3` | Replication factor |
| `ssl_enabled` | `false` | Enable SSL/SASL |
| `kafka_user` | - | SASL username |
| `kafka_password` | - | SASL password |

### perf_producer Role

| Variable | Default | Description |
|----------|---------|-------------|
| `perf_num_records` | `1000000` | Records to produce |
| `perf_record_size` | `1024` | Message size (bytes) |
| `perf_throughput` | `-1` | Target throughput (-1 = unlimited) |
| `perf_acks` | `"1"` | Acknowledgment setting |
| `perf_batch_size` | `16384` | Batch size (bytes) |
| `perf_linger_ms` | `10` | Linger time (ms) |
| `perf_compression_type` | `zstd` | Compression algorithm |
| `perf_buffer_memory` | `67108864` | Buffer memory (64 MB) |
| `perf_max_inflight` | `5` | Max in-flight requests |
| `producer_async_timeout` | `80000` | Async timeout (ms) |

### perf_consumer Role

| Variable | Default | Description |
|----------|---------|-------------|
| `perf_num_messages` | `1000000` | Messages to consume |
| `perf_consumer_timeout` | `80000` | Consumer timeout (ms) |
| `perf_fetch_min_bytes` | `10240` | Min fetch bytes |
| `perf_fetch_max_wait_ms` | `100` | Max fetch wait (ms) |
| `perf_max_poll_records` | `500` | Max poll records |
| `perf_receive_buffer_bytes` | `1048576` | Receive buffer (1 MB) |
| `perf_consumer_group` | `perf-consumer-group` | Consumer group ID |

### log_parser Role

| Variable | Default | Description |
|----------|---------|-------------|
| `scripts_dir` | `{{ playbook_dir }}/../../../scripts` | Scripts directory |
| `python_venv` | `{{ playbook_dir }}/../../../venv` | Virtual environment |
| `use_venv` | `true` | Use virtual environment |
| `parser_verbose` | `false` | Verbose output |

### excel_generator Role

| Variable | Default | Description |
|----------|---------|-------------|
| `report_filename` | Auto-generated | Report filename |
| `generator_verbose` | `false` | Verbose output |

### cleanup Role

| Variable | Default | Description |
|----------|---------|-------------|
| `delete_test_topics` | `true` | Delete topics after test |
| `archive_logs` | `false` | Archive raw logs |
| `remove_temp_files` | `true` | Remove temp configs |

## Playbook Variables

### full_benchmark.yml

| Variable | Default | Description |
|----------|---------|-------------|
| `run_producer_baseline` | `true` | Run producer tests |
| `run_consumer_baseline` | `true` | Run consumer tests |
| `run_load_scaling` | `true` | Run scaling tests |
| `run_message_size` | `true` | Run message size tests |
| `run_acks_tradeoff` | `true` | Run acks tests |
| `generate_report` | `true` | Generate Excel report |
| `test_profile` | `quick` | Test profile to use |

## Directory Configuration

### Results Structure

| Variable | Default | Description |
|----------|---------|-------------|
| `results_base_dir` | `{{ playbook_dir }}/../../../results` | Results root |
| `raw_logs_dir` | `{{ results_base_dir }}/raw_logs` | Raw log output |
| `parsed_data_dir` | `{{ results_base_dir }}/parsed_data` | Parsed JSON |
| `reports_dir` | `{{ results_base_dir }}/reports` | Excel reports |

## Override Examples

### Via Command Line

```bash
# Change record count
ansible-playbook playbooks/producer_baseline.yml \
  -e "perf_num_records=5000000"

# Use baseline profile
ansible-playbook playbooks/producer_baseline.yml \
  -e "test_profile=baseline"

# Enable SSL
ansible-playbook playbooks/producer_baseline.yml \
  -e "ssl_enabled=true" \
  -e "kafka_user=myuser" \
  -e "kafka_password=mypass"
```

### Via Extra Vars File

Create `my_vars.yml`:
```yaml
perf_num_records: 5000000
test_profile: baseline
ssl_enabled: true
```

Run with:
```bash
ansible-playbook playbooks/producer_baseline.yml \
  -e "@my_vars.yml"
```
