# Troubleshooting Guide

Common issues and solutions when running Kafka performance tests.

## Quick Diagnostics

```bash
# Check Ansible connectivity
ansible -i examples/inventory/dev all -m ping

# Verify Kafka tools
ansible -i examples/inventory/dev all -m shell -a "ls /usr/local/bin/kafka-*"

# Check Python environment
source venv/bin/activate
python -c "import openpyxl, pandas, numpy; print('OK')"

# Dry run a playbook
ansible-playbook -i examples/inventory/dev playbooks/producer_baseline.yml --check
```

---

## Connection Issues

### SSH Connection Failed

**Symptom:**
```
UNREACHABLE! => {"changed": false, "msg": "Failed to connect to the host via ssh"}
```

**Solutions:**
1. Verify SSH key:
   ```bash
   ssh -i ~/.ssh/your-key user@broker-host
   ```

2. Check inventory:
   ```yaml
   # examples/inventory/dev/hosts.yml
   kafka-broker-1:
     ansible_host: correct-hostname.example.com
     ansible_user: correct-user
     ansible_ssh_private_key_file: ~/.ssh/correct-key
   ```

3. Disable host key checking (temporary):
   ```bash
   export ANSIBLE_HOST_KEY_CHECKING=False
   ```

### Kafka Broker Unreachable

**Symptom:**
```
TASK [setup_environment : Create test topic] FAILED
Connection to node -1 could not be established
```

**Solutions:**
1. Verify broker addresses:
   ```yaml
   kafka_broker:
     hosts:
       - broker1.example.com:9092  # Check port
   ```

2. Test connectivity:
   ```bash
   nc -zv broker1.example.com 9092
   ```

3. Check firewall rules

4. For SSL clusters, verify SSL config:
   ```yaml
   ssl_enabled: true
   kafka_user: "your-user"
   kafka_password: "your-password"
   ```

---

## Test Execution Issues

### Kafka Tools Not Found

**Symptom:**
```
TASK [setup_environment : Verify Kafka CLI tools] FAILED
stat: path: /usr/local/bin/kafka-producer-perf-test.sh does not exist
```

**Solutions:**
1. Set correct Kafka path:
   ```yaml
   kafka_home: "/opt/kafka"  # Or your installation path
   binary_base_path: "{{ kafka_home }}"
   ```

2. Verify tools exist:
   ```bash
   find / -name "kafka-producer-perf-test*" 2>/dev/null
   ```

### Topic Creation Fails

**Symptom:**
```
TASK [setup_environment : Create test topic] FAILED
Error: Replication factor: 3 larger than available brokers: 1
```

**Solutions:**
1. Reduce replication factor:
   ```yaml
   perf_replication_factor: 1  # Match available brokers
   ```

2. Or specify in command:
   ```bash
   ansible-playbook playbooks/producer_baseline.yml \
     -e "perf_replication_factor=1"
   ```

### Async Job Timeout

**Symptom:**
```
TASK [perf_producer : Wait for producer completion] FAILED
Timeout waiting for async job
```

**Solutions:**
1. Increase timeout:
   ```yaml
   producer_async_timeout: 120000  # 2 minutes
   ```

2. Reduce record count:
   ```bash
   ansible-playbook playbooks/producer_baseline.yml \
     -e "perf_num_records=100000"
   ```

3. Check broker performance (may be slow)

### SSL/SASL Authentication Errors

**Symptom:**
```
Authentication failed: SASL authentication failed
```

**Solutions:**
1. Verify credentials:
   ```yaml
   ssl_enabled: true
   kafka_user: "correct-username"
   kafka_password: "correct-password"
   ```

2. Check SASL mechanism matches cluster:
   - Default is `PLAIN`
   - May need `SCRAM-SHA-256` or `SCRAM-SHA-512`

---

## Parsing Issues

### Log Parser Fails

**Symptom:**
```
TASK [log_parser : Run log parser script] FAILED
```

**Solutions:**
1. Verify Python environment:
   ```bash
   source venv/bin/activate
   python scripts/parse_perf_logs.py --help
   ```

2. Check log files exist:
   ```bash
   ls -la results/raw_logs/*.log
   ```

3. Run parser manually:
   ```bash
   python scripts/parse_perf_logs.py \
     results/raw_logs \
     results/parsed_data \
     --verbose
   ```

### No Metrics Parsed

**Symptom:**
```
[WARN] No producer metrics found in producer_test.log
```

**Causes:**
- Log file empty or truncated
- Unexpected log format
- Test didn't produce expected output

**Solutions:**
1. Check raw log content:
   ```bash
   cat results/raw_logs/producer_*.log
   ```

2. Look for the expected pattern:
   ```
   X records sent, Y records/sec (Z MB/sec), ...
   ```

3. If format differs, update regex in `parse_perf_logs.py`

---

## Excel Generation Issues

### Excel Generator Fails

**Symptom:**
```
TASK [excel_generator : Run Excel generator script] FAILED
```

**Solutions:**
1. Verify dependencies:
   ```bash
   pip install openpyxl pandas numpy
   ```

2. Check parsed JSON exists:
   ```bash
   ls results/parsed_data/*.json
   ```

3. Run generator manually:
   ```bash
   python scripts/generate_excel_report.py \
     results/parsed_data/parsed_results_*.json \
     results/reports/test.xlsx \
     --verbose
   ```

### Empty Excel Report

**Symptom:**
- Report generated but sheets are empty

**Causes:**
- No data in parsed JSON
- Parsing failed silently

**Solutions:**
1. Check parsed JSON:
   ```bash
   cat results/parsed_data/parsed_results_*.json | python -m json.tool
   ```

2. Verify log files were created during tests

---

## Performance Issues

### Tests Running Too Slow

**Solutions:**
1. Use quick profile:
   ```bash
   ansible-playbook playbooks/producer_baseline.yml \
     -e "test_profile=quick"
   ```

2. Reduce record count:
   ```bash
   ansible-playbook playbooks/producer_baseline.yml \
     -e "perf_num_records=100000"
   ```

3. Reduce test matrix:
   ```yaml
   # test_matrices.yml
   producer_test_matrix:
     quick:
       acks: ["1"]  # Fewer values
       batch_size: [16384]
   ```

### Inconsistent Results

**Causes:**
- Cluster not idle
- Network interference
- Resource contention

**Solutions:**
1. Run tests during off-peak hours
2. Run multiple iterations
3. Use aggregation script:
   ```bash
   python scripts/aggregate_results.py \
     results/parsed_data \
     results/aggregated.json \
     --print-summary
   ```

---

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `No JSON files found` | Parsing didn't run or failed | Check raw logs exist |
| `Topic already exists` | Previous test didn't clean up | Add `--force` or delete manually |
| `Connection refused` | Wrong port or firewall | Check broker connectivity |
| `LEADER_NOT_AVAILABLE` | Topic not ready | Increase topic create delay |
| `PermissionDenied` | SSH/sudo issues | Check user permissions |

---

## Getting Help

### Gather Diagnostic Info

```bash
# Ansible version
ansible --version

# Python version
python --version

# Installed packages
pip list

# Directory structure
find . -type f -name "*.log" -o -name "*.json" 2>/dev/null

# Last error logs
tail -50 results/raw_logs/*.log
```

### Debug Mode

Run with verbose output:
```bash
ansible-playbook playbooks/producer_baseline.yml -vvv
```

### File an Issue

Include:
1. Ansible version
2. Python version
3. Error message (full)
4. Inventory configuration (redacted)
5. Command used
6. Relevant log files

Submit at: https://github.com/osodevops/kafka-performance-testing/issues
