# Kafka Performance Testing Automation PRD

**Author:** OSO DevOps  
**Date:** December 2024  
**Status:** For Implementation  
**Target Repository:** [kafka-performance-testing](https://github.com/osodevops/kafka-performance-testing)

---

## Executive Summary

This Product Requirements Document outlines the enhancement of the OSO Kafka performance testing Ansible playbook to automate comprehensive performance testing, structured log capture, and Excel-based visualization. The system will enable teams to quickly identify optimal Kafka configuration settings through repeatable, data-driven benchmarking.

### Key Objectives
- Automate multi-scenario performance testing via enhanced Ansible playbook
- Parse and structure raw `kafka-producer-perf-test` and `kafka-consumer-perf-test` outputs
- Export results to Excel with dynamic graphs for performance visualization
- Enable easy parameter variation and result comparison
- Identify optimal settings across throughput, latency, and resource utilization

---

## 1. Testing Strategy & Scope

### 1.1 Performance Dimensions

The playbook must test and measure across four critical dimensions:

| Dimension | Metrics | Tools |
|-----------|---------|-------|
| **Throughput** | Records/sec, MB/sec | kafka-producer-perf-test, kafka-consumer-perf-test |
| **Latency** | Avg ms, P50, P95, P99, P99.9 | Built-in percentile output |
| **Resource Utilization** | Network I/O, Disk I/O, Memory, CPU | System monitoring (iostat, sar, jstat) |
| **Scalability** | Linear degradation with load | Multi-producer/consumer tests |

### 1.2 Test Scenarios

The playbook should execute the following test matrix automatically:

#### Scenario 1: Producer Configuration Baseline
**Purpose:** Identify optimal producer settings  
**Variables to iterate:**
- `acks`: [0, 1, all]
- `batch.size`: [1024, 8192, 16384, 32768, 64000]
- `linger.ms`: [0, 5, 10, 20, 50]
- `compression.type`: [none, snappy, lz4, zstd]
- `record.size`: [512, 1024, 2048, 4096]

**Fixed parameters:**
- `num.records`: 1,000,000 (configurable)
- `throughput`: -1 (unlimited)
- `buffer.memory`: 67,108,864 bytes
- `max.in.flight.requests.per.connection`: 5

**Output captured:**
- Final throughput (records/sec, MB/sec)
- Average latency (ms)
- Max latency (ms)
- Percentiles: 50th, 95th, 99th, 99.9th

#### Scenario 2: Consumer Configuration Baseline
**Purpose:** Identify optimal consumer settings  
**Variables to iterate:**
- `fetch.min.bytes`: [1024, 10240, 102400]
- `fetch.max.wait.ms`: [0, 50, 100, 500]
- `max.poll.records`: [100, 500, 1000, 5000]
- `receive.buffer.bytes`: [1048576, 8388608]

**Fixed parameters:**
- `messages`: 1,000,000 (match producer scenario)
- `group.id`: perf-consumer-group

**Output captured:**
- Data consumed (MB)
- Throughput (MB/sec, records/sec)
- Rebalance time (ms)
- Fetch time (ms)
- Per-message throughput (nMsg/sec)

#### Scenario 3: Load Scaling Tests
**Purpose:** Measure performance degradation under multi-producer/consumer load  
**Variables to iterate:**
- `num.producers`: [1, 3, 5, 10]
- `num.consumers`: [1, 3, 5]
- Producer run concurrently or sequentially (configurable)

**Fixed parameters:**
- Use optimal settings from Scenario 1
- `num.records.per.producer`: 1,000,000

**Output captured:**
- Per-producer/consumer throughput
- Aggregate throughput
- Total latency impact
- Resource contention signals

#### Scenario 4: Message Size Impact
**Purpose:** Understand relationship between message size and performance  
**Variables to iterate:**
- `record.size`: [128, 256, 512, 1024, 2048, 4096, 8192, 16384]
- `batch.size`: auto-scale relative to message size (e.g., 10x message size)
- `compression.type`: [none, zstd]

**Fixed parameters:**
- `acks`: 1 (fastest with reasonable durability)
- `linger.ms`: 10

**Output captured:**
- Throughput vs. message size
- Compression ratio (pre/post)
- Bytes/sec efficiency

#### Scenario 5: Acknowledgment Trade-offs
**Purpose:** Quantify durability vs. performance impact  
**Variables to iterate:**
- `acks`: [0, 1, all]
- Replication factor: [1, 3]
- `min.insync.replicas`: [1, 2, 3] (when acks=all)

**Fixed parameters:**
- `batch.size`: 16384
- `linger.ms`: 10
- `record.size`: 1024

**Output captured:**
- Throughput comparison
- Latency breakdown (network, replication, local)
- Data safety guarantees vs. performance trade-off analysis

---

## 2. Playbook Architecture & Implementation

### 2.1 Playbook Structure

The enhanced Ansible playbook should follow this structure:

```
kafka-performance-testing/
├── README.md
├── ansible.cfg
├── inventory/
│   ├── hosts
│   └── group_vars/
│       ├── brokers.yml
│       ├── producers.yml
│       └── consumers.yml
├── roles/
│   ├── setup_environment/
│   ├── perf_producer/
│   ├── perf_consumer/
│   ├── log_parser/
│   ├── excel_generator/
│   └── cleanup/
├── playbooks/
│   ├── full_benchmark.yml
│   ├── producer_baseline.yml
│   ├── consumer_baseline.yml
│   ├── load_scaling.yml
│   ├── message_size_tests.yml
│   └── acks_tradeoff.yml
├── scripts/
│   ├── parse_perf_logs.py
│   ├── generate_excel_report.py
│   ├── extract_system_metrics.sh
│   └── aggregate_results.py
├── templates/
│   ├── producer_test.j2
│   ├── consumer_test.j2
│   └── config_template.j2
└── results/
    ├── raw_logs/
    ├── parsed_data/
    └── reports/
```

### 2.2 Core Roles

#### Role: `setup_environment`
**Responsibilities:**
- Verify Kafka installation and broker connectivity
- Create test topics with specified replication factor and partitions
- Initialize monitoring (if enabled)
- Validate test infrastructure readiness

**Key tasks:**
```yaml
- name: Verify Kafka CLI tools available
  stat:
    path: "{{ kafka_home }}/bin/kafka-producer-perf-test.sh"
  
- name: Create test topic
  shell: |
    {{ kafka_home }}/bin/kafka-topics.sh \
      --create \
      --topic perf-test-{{ scenario_name }} \
      --bootstrap-server {{ brokers }} \
      --partitions {{ num_partitions }} \
      --replication-factor {{ replication_factor }} \
      --if-not-exists
      
- name: Validate broker connectivity
  shell: |
    {{ kafka_home }}/bin/kafka-broker-api-versions.sh \
      --bootstrap-server {{ brokers }}
```

#### Role: `perf_producer`
**Responsibilities:**
- Execute producer performance tests with parameter variations
- Capture full output including statistics
- Log system metrics during test
- Handle parallel execution of multiple producers

**Key tasks:**
```yaml
- name: Run producer performance test
  shell: |
    {{ kafka_home }}/bin/kafka-producer-perf-test.sh \
      --topic {{ topic }} \
      --num-records {{ num_records }} \
      --record-size {{ record_size }} \
      --throughput {{ throughput }} \
      --producer-props \
        bootstrap.servers={{ brokers }} \
        batch.size={{ batch_size }} \
        linger.ms={{ linger_ms }} \
        acks={{ acks }} \
        compression.type={{ compression_type }} \
        buffer.memory={{ buffer_memory }} \
        max.in.flight.requests.per.connection={{ max_inflight }} \
      --print-metrics 2>&1
  register: producer_output
  
- name: Save producer output
  copy:
    content: |
      # Producer Test - {{ scenario_name }}
      # Configuration: acks={{ acks }}, batch.size={{ batch_size }}, linger.ms={{ linger_ms }}, compression={{ compression_type }}
      # Record Size: {{ record_size }} bytes
      # Test Date: {{ ansible_date_time.iso8601 }}
      
      {{ producer_output.stdout }}
    dest: "{{ log_dir }}/producer_{{ scenario_name }}_{{ timestamp }}.log"
```

#### Role: `perf_consumer`
**Responsibilities:**
- Execute consumer performance tests
- Coordinate with producer completion
- Capture consumption metrics
- Measure end-to-end latency if applicable

**Key tasks:**
```yaml
- name: Run consumer performance test
  shell: |
    {{ kafka_home }}/bin/kafka-consumer-perf-test.sh \
      --topic {{ topic }} \
      --messages {{ num_messages }} \
      --bootstrap-server {{ brokers }} \
      --consumer.config {{ consumer_config }} \
      --print-metrics 2>&1
  register: consumer_output
  
- name: Extract and save consumer metrics
  copy:
    content: |
      # Consumer Test - {{ scenario_name }}
      # Configuration: fetch.min.bytes={{ fetch_min_bytes }}, max.poll.records={{ max_poll_records }}
      # Test Date: {{ ansible_date_time.iso8601 }}
      
      {{ consumer_output.stdout }}
    dest: "{{ log_dir }}/consumer_{{ scenario_name }}_{{ timestamp }}.log"
```

#### Role: `log_parser`
**Responsibilities:**
- Parse all performance test logs using Python
- Extract key metrics using regex patterns
- Normalize and validate data
- Output structured JSON/CSV

**Implementation:** See Section 3

#### Role: `excel_generator`
**Responsibilities:**
- Read parsed JSON/CSV data
- Generate Excel workbook with multiple sheets
- Create pivot tables and charts
- Implement automated recommendation logic

**Implementation:** See Section 4

#### Role: `cleanup`
**Responsibilities:**
- Delete test topics
- Archive raw logs
- Remove temporary files
- Optional: Clean up test infrastructure

---

## 3. Log Parsing Strategy

### 3.1 Output Patterns to Parse

The Kafka perf tools output follows consistent patterns:

#### Producer Output Pattern
```
[NUM] records sent, [THROUGHPUT_RPS] records/sec ([THROUGHPUT_MB] MB/sec), [AVG_LAT] ms avg latency, [MAX_LAT] ms max latency.
[FINAL_NUM] records sent, [FINAL_RPS] records/sec ([FINAL_MB] MB/sec), [FINAL_AVG_LAT] ms avg latency, [FINAL_MAX_LAT] ms max latency, [P50] ms 50th, [P95] ms 95th, [P99] ms 99th, [P999] ms 99.9th.
```

**Example:**
```
1000000 records sent, 14637.645096 records/sec (28.59 MB/sec), 3182.27 ms avg latency, 3613.00 ms max latency, 3289 ms 50th, 3467 ms 95th, 3568 ms 99th, 3603 ms 99.9th.
```

#### Consumer Output Pattern
```
start.time, end.time, data.consumed.in.MB, MB.sec, data.consumed.in.nMsg, nMsg.sec, rebalance.time.ms, fetch.time.ms, fetch.MB.sec, fetch.nMsg.sec
[START_TIME], [END_TIME], [MB_CONSUMED], [MB_SEC], [NUM_MSGS], [MSG_SEC], [REBALANCE_MS], [FETCH_MS], [FETCH_MB_SEC], [FETCH_MSG_SEC]
```

**Example:**
```
2024-08-28 12:00:45:269, 2024-08-28 12:01:53:199, 1953.1250, 28.7520, 1000000, 14721.0364, 3330, 64600, 30.2341, 15479.8762
```

### 3.2 Python Log Parser Implementation

**Location:** `scripts/parse_perf_logs.py`

**Responsibilities:**
1. Recursively scan log directory
2. Parse producer and consumer logs separately
3. Extract all metrics with associated configuration
4. Validate data integrity
5. Output structured JSON files

**Pseudo-code:**
```python
import re
import json
import os
from pathlib import Path
from datetime import datetime

class KafkaPerformanceParser:
    def __init__(self, log_dir, output_dir):
        self.log_dir = log_dir
        self.output_dir = output_dir
        self.producer_pattern = re.compile(
            r'(\d+) records sent, ([\d.]+) records/sec \(([\d.]+) MB/sec\), '
            r'([\d.]+) ms avg latency, ([\d.]+) ms max latency, '
            r'([\d]+) ms 50th, ([\d]+) ms 95th, ([\d]+) ms 99th, ([\d]+) ms 99\.9th'
        )
        self.consumer_pattern = re.compile(
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}:\d{3}), '
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}:\d{3}), '
            r'([\d.]+), ([\d.]+), (\d+), ([\d.]+), (\d+), (\d+), ([\d.]+), ([\d.]+)'
        )
    
    def parse_producer_log(self, filepath):
        """Extract configuration and metrics from producer log"""
        config = self._extract_config_from_filename(filepath)
        metrics = []
        
        with open(filepath, 'r') as f:
            content = f.read()
            
            # Extract metadata from header comments
            for line in content.split('\n'):
                if line.startswith('#'):
                    self._parse_config_line(line, config)
            
            # Find final summary line (last match)
            matches = list(self.producer_pattern.finditer(content))
            if matches:
                final_match = matches[-1]
                metrics = {
                    'records_sent': int(final_match.group(1)),
                    'throughput_rps': float(final_match.group(2)),
                    'throughput_mb': float(final_match.group(3)),
                    'avg_latency_ms': float(final_match.group(4)),
                    'max_latency_ms': float(final_match.group(5)),
                    'p50_ms': int(final_match.group(6)),
                    'p95_ms': int(final_match.group(7)),
                    'p99_ms': int(final_match.group(8)),
                    'p999_ms': int(final_match.group(9)),
                }
        
        return {
            'test_type': 'producer',
            'configuration': config,
            'metrics': metrics,
            'filepath': filepath,
            'parse_time': datetime.now().isoformat()
        }
    
    def parse_consumer_log(self, filepath):
        """Extract metrics from consumer log"""
        config = self._extract_config_from_filename(filepath)
        metrics = {}
        
        with open(filepath, 'r') as f:
            lines = f.readlines()
            
            # Find data line (skip header)
            for i, line in enumerate(lines):
                if not line.startswith('start.time') and ',' in line:
                    match = self.consumer_pattern.search(line)
                    if match:
                        metrics = {
                            'start_time': match.group(1),
                            'end_time': match.group(2),
                            'data_consumed_mb': float(match.group(3)),
                            'throughput_mb_sec': float(match.group(4)),
                            'num_messages': int(match.group(5)),
                            'throughput_msg_sec': float(match.group(6)),
                            'rebalance_time_ms': int(match.group(7)),
                            'fetch_time_ms': int(match.group(8)),
                            'fetch_mb_sec': float(match.group(9)),
                            'fetch_msg_sec': float(match.group(10)),
                        }
                        break
        
        return {
            'test_type': 'consumer',
            'configuration': config,
            'metrics': metrics,
            'filepath': filepath,
            'parse_time': datetime.now().isoformat()
        }
    
    def parse_all_logs(self):
        """Parse all log files in directory"""
        all_results = []
        
        for log_file in Path(self.log_dir).glob('*.log'):
            try:
                if 'producer' in log_file.name:
                    result = self.parse_producer_log(str(log_file))
                elif 'consumer' in log_file.name:
                    result = self.parse_consumer_log(str(log_file))
                else:
                    continue
                
                all_results.append(result)
            except Exception as e:
                print(f"Error parsing {log_file}: {e}")
        
        return all_results
    
    def _extract_config_from_filename(self, filepath):
        """Extract test scenario and configuration from filename"""
        # Example: producer_baseline_acks_all_batch_16384_linger_10.log
        filename = Path(filepath).stem
        parts = filename.split('_')
        
        config = {
            'scenario': parts[1] if len(parts) > 1 else 'unknown',
        }
        
        # Parse key=value pairs from filename
        for i in range(2, len(parts), 2):
            if i + 1 < len(parts):
                config[parts[i]] = parts[i + 1]
        
        return config
    
    def _parse_config_line(self, line, config_dict):
        """Extract configuration from comment lines"""
        if 'Configuration:' in line:
            # Example: # Configuration: acks=all, batch.size=16384, linger.ms=10
            config_str = line.split('Configuration:')[1].strip()
            for item in config_str.split(','):
                key, value = item.strip().split('=')
                config_dict[key.strip()] = value.strip()
    
    def save_results(self, results):
        """Save parsed results to JSON"""
        output_file = os.path.join(self.output_dir, f'parsed_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        return output_file

# Usage
if __name__ == '__main__':
    import sys
    log_dir = sys.argv[1] if len(sys.argv) > 1 else './logs'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else './parsed'
    
    parser = KafkaPerformanceParser(log_dir, output_dir)
    results = parser.parse_all_logs()
    output_file = parser.save_results(results)
    print(f"Parsed {len(results)} log files. Results saved to {output_file}")
```

### 3.3 Output Format

Parsed results saved as JSON:
```json
{
  "test_type": "producer",
  "configuration": {
    "scenario": "baseline",
    "acks": "all",
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
  "filepath": "./logs/producer_baseline_acks_all_batch_16384.log",
  "parse_time": "2024-12-16T15:58:00"
}
```

---

## 4. Excel Report Generation

### 4.1 Report Structure

The Excel workbook should contain the following sheets:

| Sheet Name | Purpose | Content |
|-----------|---------|---------|
| **Summary** | Executive overview | Key findings, optimal configs, recommendations |
| **Producer Baseline** | Producer optimization results | All producer test results with charts |
| **Consumer Baseline** | Consumer optimization results | All consumer test results with charts |
| **Load Scaling** | Multi-producer/consumer impact | Throughput degradation curves |
| **Message Size Analysis** | Size vs. performance | Charts showing MB/sec and compression impact |
| **Acknowledgment Trade-offs** | Durability vs. performance | acks=0 vs acks=1 vs acks=all comparison |
| **Raw Data** | Complete data dump | Pivot table source data |
| **Recommendations** | Actionable insights | Scoring matrix for optimal settings |

### 4.2 Python Excel Generator

**Location:** `scripts/generate_excel_report.py`

**Dependencies:**
```
openpyxl>=3.0.0
pandas>=1.3.0
matplotlib>=3.5.0
numpy>=1.20.0
```

**Pseudo-code:**
```python
import openpyxl
from openpyxl.chart import LineChart, BarChart, ScatterChart, Reference
from openpyxl.utils.dataframe import dataframe_to_rows
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

class KafkaPerformanceReporter:
    def __init__(self, parsed_json_file, output_xlsx):
        self.data = self._load_parsed_data(parsed_json_file)
        self.wb = openpyxl.Workbook()
        self.wb.remove(self.wb.active)  # Remove default sheet
        self.output_file = output_xlsx
        
        # Organize data by test type
        self.producer_results = [r for r in self.data if r['test_type'] == 'producer']
        self.consumer_results = [r for r in self.data if r['test_type'] == 'consumer']
    
    def _load_parsed_data(self, json_file):
        with open(json_file, 'r') as f:
            return json.load(f)
    
    def generate_report(self):
        """Generate complete Excel report"""
        self.create_summary_sheet()
        self.create_producer_sheet()
        self.create_consumer_sheet()
        self.create_load_scaling_sheet()
        self.create_message_size_sheet()
        self.create_acks_tradeoff_sheet()
        self.create_raw_data_sheet()
        self.create_recommendations_sheet()
        
        self.wb.save(self.output_file)
        print(f"Report generated: {self.output_file}")
    
    def create_summary_sheet(self):
        """Create executive summary sheet"""
        ws = self.wb.create_sheet('Summary', 0)
        
        # Title
        ws['A1'] = 'Kafka Performance Testing Report'
        ws['A1'].font = openpyxl.styles.Font(size=16, bold=True)
        ws['A2'] = f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        
        # Key metrics
        row = 4
        ws[f'A{row}'] = 'Key Findings'
        ws[f'A{row}'].font = openpyxl.styles.Font(bold=True, size=12)
        
        # Find best producer config
        best_producer = max(
            self.producer_results,
            key=lambda x: x['metrics']['throughput_mb']
        )
        
        row += 2
        ws[f'A{row}'] = 'Best Producer Configuration'
        ws[f'B{row}'] = f"Throughput: {best_producer['metrics']['throughput_mb']:.2f} MB/sec"
        ws[f'C{row}'] = f"Latency: {best_producer['metrics']['avg_latency_ms']:.2f} ms"
        
        # Configuration details
        row += 1
        for key, value in best_producer['configuration'].items():
            ws[f'A{row}'] = f"{key}:"
            ws[f'B{row}'] = value
            row += 1
        
        # Test summary counts
        row += 2
        ws[f'A{row}'] = 'Test Summary'
        ws[f'A{row}'].font = openpyxl.styles.Font(bold=True)
        row += 1
        ws[f'A{row}'] = f"Total Producer Tests: {len(self.producer_results)}"
        row += 1
        ws[f'A{row}'] = f"Total Consumer Tests: {len(self.consumer_results)}"
        
        ws.column_dimensions['A'].width = 30
        ws.column_dimensions['B'].width = 40
    
    def create_producer_sheet(self):
        """Create producer benchmark sheet with charts"""
        ws = self.wb.create_sheet('Producer Baseline')
        
        # Prepare data
        df = pd.DataFrame([
            {
                **r['configuration'],
                'throughput_rps': r['metrics']['throughput_rps'],
                'throughput_mb': r['metrics']['throughput_mb'],
                'avg_latency_ms': r['metrics']['avg_latency_ms'],
                'p95_ms': r['metrics']['p95_ms'],
                'p99_ms': r['metrics']['p99_ms'],
            }
            for r in self.producer_results
        ])
        
        # Write data
        for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), 1):
            for c_idx, value in enumerate(row, 1):
                ws.cell(row=r_idx, column=c_idx, value=value)
        
        # Create throughput chart
        chart = LineChart()
        chart.title = 'Throughput by Configuration'
        chart.style = 12
        chart.y_axis.title = 'MB/sec'
        chart.x_axis.title = 'Configuration'
        
        # Add data to chart
        data = Reference(ws, min_col=4, min_row=1, max_row=len(df)+1)
        chart.add_data(data, titles_from_data=True)
        
        ws.add_chart(chart, "A" + str(len(df) + 5))
        
        # Create latency chart
        latency_chart = BarChart()
        latency_chart.title = 'Latency Percentiles'
        latency_chart.style = 12
        latency_chart.y_axis.title = 'Milliseconds'
        
        ws.add_chart(latency_chart, "J" + str(len(df) + 5))
        
        # Set column widths
        for col in ws.columns:
            ws.column_dimensions[col[0].column_letter].width = 15
    
    def create_consumer_sheet(self):
        """Create consumer benchmark sheet"""
        ws = self.wb.create_sheet('Consumer Baseline')
        
        # Similar to producer sheet
        df = pd.DataFrame([
            {
                **r['configuration'],
                'throughput_mb_sec': r['metrics']['throughput_mb_sec'],
                'throughput_msg_sec': r['metrics']['throughput_msg_sec'],
                'rebalance_time_ms': r['metrics']['rebalance_time_ms'],
            }
            for r in self.consumer_results
        ])
        
        for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), 1):
            for c_idx, value in enumerate(row, 1):
                ws.cell(row=r_idx, column=c_idx, value=value)
        
        # Add charts similar to producer sheet
        for col in ws.columns:
            ws.column_dimensions[col[0].column_letter].width = 15
    
    def create_load_scaling_sheet(self):
        """Analyze performance degradation with multiple producers/consumers"""
        ws = self.wb.create_sheet('Load Scaling')
        
        ws['A1'] = 'Performance Degradation Analysis'
        ws['A1'].font = openpyxl.styles.Font(bold=True, size=12)
        
        # Group by number of producers
        producer_groups = {}
        for result in self.producer_results:
            num_producers = result['configuration'].get('num_producers', 1)
            if num_producers not in producer_groups:
                producer_groups[num_producers] = []
            producer_groups[num_producers].append(result)
        
        row = 3
        for num_prod in sorted(producer_groups.keys()):
            ws[f'A{row}'] = f'With {num_prod} Producer(s):'
            ws[f'A{row}'].font = openpyxl.styles.Font(bold=True)
            row += 1
            
            for result in producer_groups[num_prod]:
                ws[f'A{row}'] = f"Avg Throughput: {result['metrics']['throughput_mb']:.2f} MB/sec"
                row += 1
    
    def create_message_size_sheet(self):
        """Analyze impact of message size on performance"""
        ws = self.wb.create_sheet('Message Size Analysis')
        
        # Filter and sort by message size
        msg_size_results = sorted(
            self.producer_results,
            key=lambda x: int(x['configuration'].get('record_size', 1024))
        )
        
        ws['A1'] = 'Message Size vs. Performance'
        ws['A1'].font = openpyxl.styles.Font(bold=True, size=12)
        
        df = pd.DataFrame([
            {
                'record_size': r['configuration'].get('record_size', ''),
                'throughput_mb': r['metrics']['throughput_mb'],
                'avg_latency_ms': r['metrics']['avg_latency_ms'],
            }
            for r in msg_size_results
        ])
        
        for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), 3):
            for c_idx, value in enumerate(row, 1):
                ws.cell(row=r_idx, column=c_idx, value=value)
        
        # Create comparison chart
        chart = ScatterChart()
        chart.title = 'Message Size vs. Throughput'
        chart.x_axis.title = 'Message Size (bytes)'
        chart.y_axis.title = 'Throughput (MB/sec)'
        
        ws.add_chart(chart, "A" + str(len(df) + 7))
    
    def create_acks_tradeoff_sheet(self):
        """Analyze acks setting trade-offs"""
        ws = self.wb.create_sheet('Acknowledgment Trade-offs')
        
        ws['A1'] = 'Durability vs. Performance: acks Setting Impact'
        ws['A1'].font = openpyxl.styles.Font(bold=True, size=12)
        
        # Group by acks setting
        acks_groups = {}
        for result in self.producer_results:
            acks_val = result['configuration'].get('acks', 'unknown')
            if acks_val not in acks_groups:
                acks_groups[acks_val] = []
            acks_groups[acks_val].append(result)
        
        row = 3
        ws[f'A{row}'] = 'acks'
        ws[f'B{row}'] = 'Avg Throughput (MB/sec)'
        ws[f'C{row}'] = 'Avg Latency (ms)'
        ws[f'D{row}'] = 'Description'
        row += 1
        
        descriptions = {
            '0': 'No broker acknowledgment (fastest, least durable)',
            '1': 'Leader acknowledgment only (balanced)',
            'all': 'All replicas acknowledgment (most durable, slowest)',
        }
        
        for acks_val in sorted(acks_groups.keys()):
            results = acks_groups[acks_val]
            avg_throughput = sum(r['metrics']['throughput_mb'] for r in results) / len(results)
            avg_latency = sum(r['metrics']['avg_latency_ms'] for r in results) / len(results)
            
            ws[f'A{row}'] = acks_val
            ws[f'B{row}'] = f"{avg_throughput:.2f}"
            ws[f'C{row}'] = f"{avg_latency:.2f}"
            ws[f'D{row}'] = descriptions.get(acks_val, '')
            row += 1
        
        # Create comparison chart
        chart = BarChart()
        chart.title = 'acks Setting Performance Comparison'
        chart.x_axis.title = 'acks Setting'
        chart.y_axis.title = 'Throughput (MB/sec)'
        
        ws.add_chart(chart, "A" + str(row + 2))
    
    def create_raw_data_sheet(self):
        """Create raw data sheet for pivot tables"""
        ws = self.wb.create_sheet('Raw Data')
        
        # Combine all results
        all_results = []
        for r in self.producer_results:
            all_results.append({
                'test_type': 'producer',
                **r['configuration'],
                **r['metrics'],
            })
        
        for r in self.consumer_results:
            all_results.append({
                'test_type': 'consumer',
                **r['configuration'],
                **r['metrics'],
            })
        
        df = pd.DataFrame(all_results)
        
        for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), 1):
            for c_idx, value in enumerate(row, 1):
                ws.cell(row=r_idx, column=c_idx, value=value)
        
        # Set column widths
        for col in ws.columns:
            ws.column_dimensions[col[0].column_letter].width = 15
    
    def create_recommendations_sheet(self):
        """Create recommendations based on analysis"""
        ws = self.wb.create_sheet('Recommendations')
        
        ws['A1'] = 'Performance Optimization Recommendations'
        ws['A1'].font = openpyxl.styles.Font(bold=True, size=14)
        
        row = 3
        
        # Find optimal configurations based on different criteria
        recommendations = self._generate_recommendations()
        
        for category, items in recommendations.items():
            ws[f'A{row}'] = category
            ws[f'A{row}'].font = openpyxl.styles.Font(bold=True, size=11)
            row += 1
            
            for item in items:
                ws[f'A{row}'] = f"• {item}"
                ws.text_alignment.wrap_text = True
                row += 1
            
            row += 1
    
    def _generate_recommendations(self):
        """Generate actionable recommendations"""
        recommendations = {}
        
        # High throughput recommendation
        best_throughput = max(
            self.producer_results,
            key=lambda x: x['metrics']['throughput_mb']
        )
        recommendations['For Maximum Throughput'] = [
            f"Use acks={best_throughput['configuration'].get('acks')}",
            f"Set batch.size={best_throughput['configuration'].get('batch_size')}",
            f"Set linger.ms={best_throughput['configuration'].get('linger_ms')}",
            f"Use compression.type={best_throughput['configuration'].get('compression_type')}",
            f"Expected throughput: {best_throughput['metrics']['throughput_mb']:.2f} MB/sec",
        ]
        
        # Low latency recommendation
        best_latency = min(
            self.producer_results,
            key=lambda x: x['metrics']['avg_latency_ms']
        )
        recommendations['For Minimum Latency'] = [
            f"Use acks={best_latency['configuration'].get('acks')}",
            f"Set batch.size={best_latency['configuration'].get('batch_size')}",
            f"Set linger.ms={best_latency['configuration'].get('linger_ms')}",
            f"Expected latency: {best_latency['metrics']['avg_latency_ms']:.2f} ms",
        ]
        
        # Balanced recommendation
        balanced = self._find_balanced_config()
        if balanced:
            recommendations['For Balanced Performance'] = [
                f"Use acks={balanced['configuration'].get('acks')}",
                f"Set batch.size={balanced['configuration'].get('batch_size')}",
                f"Set linger.ms={balanced['configuration'].get('linger_ms')}",
                f"Throughput: {balanced['metrics']['throughput_mb']:.2f} MB/sec, Latency: {balanced['metrics']['avg_latency_ms']:.2f} ms",
            ]
        
        return recommendations
    
    def _find_balanced_config(self):
        """Find configuration that balances throughput and latency"""
        # Score each result: higher is better
        # Normalize throughput (higher is better) and latency (lower is better)
        
        if not self.producer_results:
            return None
        
        max_throughput = max(r['metrics']['throughput_mb'] for r in self.producer_results)
        max_latency = max(r['metrics']['avg_latency_ms'] for r in self.producer_results)
        
        best_score = -1
        best_result = None
        
        for result in self.producer_results:
            throughput_score = result['metrics']['throughput_mb'] / max_throughput
            latency_score = 1 - (result['metrics']['avg_latency_ms'] / max_latency)
            
            # Weighted average: 60% throughput, 40% latency
            score = (0.6 * throughput_score) + (0.4 * latency_score)
            
            if score > best_score:
                best_score = score
                best_result = result
        
        return best_result

# Usage
if __name__ == '__main__':
    import sys
    parsed_json = sys.argv[1] if len(sys.argv) > 1 else './parsed/parsed_results.json'
    output_xlsx = sys.argv[2] if len(sys.argv) > 2 else './reports/kafka_perf_report.xlsx'
    
    reporter = KafkaPerformanceReporter(parsed_json, output_xlsx)
    reporter.generate_report()
```

### 4.3 Chart Types & Visualizations

Each sheet includes optimized visualizations:

- **Line Charts:** Throughput/latency trends across parameter variations
- **Bar Charts:** Comparisons between discrete settings (e.g., acks values)
- **Scatter Plots:** Message size vs. throughput/latency
- **Heatmaps:** Multi-dimensional analysis (optional, requires additional library)
- **Trend Lines:** Performance degradation curves for scaling tests

---

## 5. Ansible Playbook Integration

### 5.1 Main Orchestration Playbook

**Location:** `playbooks/full_benchmark.yml`

```yaml
---
- name: Complete Kafka Performance Benchmark
  hosts: localhost
  vars:
    kafka_home: "/opt/kafka"
    brokers: "broker1:9093,broker2:9093,broker3:9093"
    log_dir: "./results/raw_logs"
    parsed_dir: "./results/parsed_data"
    report_dir: "./results/reports"
    timestamp: "{{ ansible_date_time.iso8601 }}"
  
  tasks:
    - name: Create result directories
      file:
        path: "{{ item }}"
        state: directory
        mode: '0755'
      loop:
        - "{{ log_dir }}"
        - "{{ parsed_dir }}"
        - "{{ report_dir }}"
    
    - name: Setup test environment
      include_role:
        name: setup_environment
    
    - name: Run producer baseline tests
      include_role:
        name: perf_producer
      vars:
        scenario_name: "producer_baseline_{{ item.acks }}_{{ item.batch_size }}_{{ item.linger_ms }}"
        acks: "{{ item.acks }}"
        batch_size: "{{ item.batch_size }}"
        linger_ms: "{{ item.linger_ms }}"
        compression_type: "{{ item.compression_type }}"
        record_size: "{{ item.record_size }}"
      loop:
        - { acks: '1', batch_size: 16384, linger_ms: 10, compression_type: 'zstd', record_size: 1024 }
        - { acks: '1', batch_size: 32768, linger_ms: 10, compression_type: 'zstd', record_size: 1024 }
        - { acks: '1', batch_size: 16384, linger_ms: 20, compression_type: 'zstd', record_size: 1024 }
        - { acks: '1', batch_size: 8192, linger_ms: 5, compression_type: 'lz4', record_size: 1024 }
        # ... additional configurations
      register: producer_tests
    
    - name: Run consumer baseline tests
      include_role:
        name: perf_consumer
      vars:
        scenario_name: "consumer_baseline_{{ item.fetch_min_bytes }}_{{ item.max_poll_records }}"
        fetch_min_bytes: "{{ item.fetch_min_bytes }}"
        max_poll_records: "{{ item.max_poll_records }}"
      loop:
        - { fetch_min_bytes: 10240, max_poll_records: 500 }
        - { fetch_min_bytes: 10240, max_poll_records: 1000 }
        - { fetch_min_bytes: 102400, max_poll_records: 5000 }
      register: consumer_tests
    
    - name: Parse all performance logs
      include_role:
        name: log_parser
    
    - name: Generate Excel report
      include_role:
        name: excel_generator
    
    - name: Cleanup test infrastructure
      include_role:
        name: cleanup
    
    - name: Display summary
      debug:
        msg: |
          Performance testing complete!
          
          Results:
          - Producer tests run: {{ producer_tests.results | length }}
          - Consumer tests run: {{ consumer_tests.results | length }}
          - Parsed data: {{ parsed_dir }}/parsed_results_*.json
          - Excel report: {{ report_dir }}/kafka_perf_report.xlsx
```

### 5.2 Running Specific Scenarios

Users can run individual test scenarios:

```bash
# Run only producer baseline
ansible-playbook playbooks/producer_baseline.yml

# Run only consumer baseline
ansible-playbook playbooks/consumer_baseline.yml

# Run load scaling tests
ansible-playbook playbooks/load_scaling.yml -e "num_producers=5 num_consumers=3"

# Run specific message size tests
ansible-playbook playbooks/message_size_tests.yml -e "start_size=512 end_size=8192"
```

---

## 6. Workflow & Usage

### 6.1 Quick Start

```bash
# Clone repository
git clone https://github.com/osodevops/kafka-performance-testing.git
cd kafka-performance-testing

# Configure inventory
vi inventory/hosts

# Run full benchmark
ansible-playbook playbooks/full_benchmark.yml

# Monitor progress
tail -f results/raw_logs/*.log

# View report (post-completion)
open results/reports/kafka_perf_report.xlsx
```

### 6.2 Advanced Usage

#### Run specific test scenarios
```bash
# Producer optimization only
ansible-playbook playbooks/full_benchmark.yml --tags "producer"

# Load scaling tests only (vary producer count)
ansible-playbook playbooks/full_benchmark.yml --tags "scaling" -e "num_producers=10"

# Message size analysis (512B to 16KB)
ansible-playbook playbooks/message_size_tests.yml
```

#### Custom parameters
```bash
# Test specific configurations
ansible-playbook playbooks/producer_baseline.yml \
  -e "acks_values=[0,1,all]" \
  -e "batch_sizes=[8192,16384,32768,64000]" \
  -e "linger_values=[5,10,20,50]" \
  -e "compression_types=[none,snappy,lz4,zstd]"
```

#### Resume interrupted runs
```bash
# Parse existing logs without re-running tests
ansible-playbook playbooks/full_benchmark.yml \
  --tags "parse,report" \
  --skip-tags "producer,consumer"
```

---

## 7. Metrics & Success Criteria

### 7.1 Key Performance Indicators

For each test run, capture and report:

| Metric | Producer | Consumer | Notes |
|--------|----------|----------|-------|
| **Throughput** | records/sec, MB/sec | records/sec, MB/sec | Higher is better |
| **Latency** | avg, p50, p95, p99, p99.9 ms | N/A | Lower is better |
| **Resource Utilization** | CPU%, Mem%, I/O wait | CPU%, Mem%, I/O wait | Monitor during test |
| **Stability** | Max latency spike | Rebalance time | Consistency matters |
| **Scalability** | Degradation with load | Degradation with load | Linear vs. exponential |

### 7.2 Success Criteria

- ✅ All test scenarios execute successfully
- ✅ Logs parse with 100% accuracy
- ✅ Excel report generates without errors
- ✅ Charts render correctly with all data points
- ✅ Recommendations are actionable and specific
- ✅ Report identifies clear performance trade-offs
- ✅ Baseline established for future comparisons

---

## 8. Implementation Timeline

### Phase 1: Foundation (Week 1-2)
- [ ] Enhance Ansible playbook structure
- [ ] Implement setup_environment and cleanup roles
- [ ] Create log parser Python script
- [ ] Test with single producer/consumer scenario

### Phase 2: Expansion (Week 3-4)
- [ ] Implement all five test scenarios
- [ ] Add parallel execution for multiple producers/consumers
- [ ] Integrate system metric collection
- [ ] Test on target Kafka cluster

### Phase 3: Reporting (Week 5)
- [ ] Implement Excel generator with all sheets
- [ ] Create charts and visualizations
- [ ] Generate recommendations engine
- [ ] End-to-end testing

### Phase 4: Polish (Week 6)
- [ ] Documentation and README
- [ ] GitHub Actions CI/CD integration
- [ ] Performance optimization for large test runs
- [ ] User acceptance testing

---

## 9. Dependencies & Tools

### 9.1 Required Software

- **Apache Kafka:** ≥ 2.8.x (for CLI tools)
- **Ansible:** ≥ 2.10
- **Python:** ≥ 3.8
- **Bash/Shell:** For scripting

### 9.2 Python Packages

```
openpyxl>=3.0.0
pandas>=1.3.0
matplotlib>=3.5.0
numpy>=1.20.0
```

### 9.3 System Requirements

- **Storage:** Minimum 100GB for test data and logs
- **Network:** Direct access to all Kafka brokers
- **Permissions:** SSH access to test infrastructure, administrative access to Kafka

---

## 10. Monitoring & Troubleshooting

### 10.1 Real-time Monitoring

During test execution:
```bash
# Watch log generation
watch "ls -lh results/raw_logs/ | tail -20"

# Monitor Kafka broker load
watch "jps | grep Kafka"

# Check disk usage
watch "df -h"

# Monitor network
watch "iftop -i eth0"
```

### 10.2 Common Issues

| Issue | Cause | Resolution |
|-------|-------|-----------|
| Logs not parsing | Unexpected log format | Verify log samples, update regex patterns |
| Excel generation fails | Missing dependencies | Install: `pip install -r requirements.txt` |
| Tests hang | Network issues to brokers | Verify broker connectivity, check firewall |
| Inconsistent results | Too many concurrent tests | Reduce parallel producers/consumers |

---

## 11. Future Enhancements

- [ ] Real-time dashboard (Grafana integration)
- [ ] Historical trend analysis (multi-run comparisons)
- [ ] Automated tuning recommendations using ML
- [ ] Integration with CI/CD pipelines
- [ ] CloudWatch/Datadog metrics export
- [ ] Kubernetes operator for distributed testing
- [ ] REST API for programmatic access
- [ ] WebUI for parameter configuration

---

## 12. References & Resources

- [OSO Kafka Performance Testing (GitHub)](https://github.com/osodevops/kafka-performance-testing)
- [Confluent Kafka Performance Testing Guide](https://confluent.io/learn/kafka-performance-testing/)
- [Kafka CLI Tools Documentation](https://kafka.apache.org/documentation/)
- [Apache Kafka Best Practices](https://kafka.apache.org/documentation/#bestpractices)
- [Kafka Performance Metrics (Datadog)](https://www.datadoghq.com/blog/monitoring-kafka-performance-metrics/)

---

## Appendix A: Sample Configuration Matrices

### Producer Configuration Matrix
```yaml
producer_configs:
  - acks: [0, 1, all]
    batch_size: [1024, 8192, 16384, 32768, 64000]
    linger_ms: [0, 5, 10, 20, 50]
    compression_type: [none, snappy, lz4, zstd]
    record_size: [512, 1024, 2048, 4096]
    max_inflight: [1, 5, 10]
    buffer_memory: [67108864]  # 64MB
```

### Consumer Configuration Matrix
```yaml
consumer_configs:
  - fetch_min_bytes: [1024, 10240, 102400]
    fetch_max_wait_ms: [0, 50, 100, 500]
    max_poll_records: [100, 500, 1000, 5000]
    receive_buffer_bytes: [1048576, 8388608]  # 1MB, 8MB
```

---

## Appendix B: Sample Excel Report Structure

The generated Excel workbook (`kafka_perf_report.xlsx`) contains:

```
Sheet 1: Summary
  - Test execution date/time
  - Cluster configuration
  - Best-performing configurations (top 3)
  - Overall recommendations
  - Executive metrics

Sheet 2-6: Detailed Analysis
  - Producer Baseline: Throughput & latency by config
  - Consumer Baseline: Throughput by config
  - Load Scaling: Performance degradation analysis
  - Message Size: Efficiency vs. size
  - Acks Trade-offs: Durability vs. performance

Sheet 7: Raw Data
  - Complete test results
  - Sortable and filterable
  - Basis for pivot tables

Sheet 8: Recommendations
  - Highest throughput settings
  - Lowest latency settings
  - Balanced settings
  - Infrastructure scaling guidance
```

---

**Document Version:** 1.0  
**Last Updated:** December 2024  
**Maintained By:** OSO DevOps Team
