# Understanding Kafka Performance Test Results

This guide explains all metrics, charts, and recommendations in the Excel performance report.

## Table of Contents

1. [Key Performance Metrics](#key-performance-metrics)
2. [Excel Report Sheets](#excel-report-sheets)
3. [Understanding Charts](#understanding-charts)
4. [The Knee Chart Explained](#the-knee-chart-explained)
5. [Scoring Methodology](#scoring-methodology)
6. [Configuration Parameters](#configuration-parameters)
7. [Interpreting Results](#interpreting-results)

---

## Key Performance Metrics

### Producer Metrics

| Metric | Description | Unit | What It Means |
|--------|-------------|------|---------------|
| **Throughput (MB/sec)** | Data volume processed per second | MB/s | Higher is better. Represents raw data transfer rate. |
| **Throughput (records/sec)** | Messages processed per second | msgs/s | Higher is better. Important for message-count workloads. |
| **Avg Latency** | Mean time from send() to acknowledgment | ms | Lower is better. Average response time. |
| **Max Latency** | Worst-case latency observed | ms | Lower is better. Important for SLA compliance. |
| **P50 Latency** | Median latency (50th percentile) | ms | Half of messages complete faster than this. |
| **P95 Latency** | 95th percentile latency | ms | 95% of messages complete faster than this. |
| **P99 Latency** | 99th percentile latency | ms | Critical for SLA. 99% of messages complete faster. |
| **P99.9 Latency** | 99.9th percentile latency | ms | Tail latency. Important for latency-sensitive apps. |

### Consumer Metrics

| Metric | Description | Unit | What It Means |
|--------|-------------|------|---------------|
| **Throughput (MB/sec)** | Data consumed per second | MB/s | Higher is better. Consumer read rate. |
| **Throughput (msgs/sec)** | Messages consumed per second | msgs/s | Higher is better. Processing rate. |
| **Fetch Rate** | How often consumer fetches data | fetches/s | Balanced is better. Too high = overhead. |
| **Rebalance Time** | Time spent in consumer group rebalance | ms | Lower is better. Impacts availability. |

### Derived Metrics

| Metric | Formula | What It Means |
|--------|---------|---------------|
| **Latency Ratio (P99/Avg)** | P99 ÷ Avg Latency | Consistency indicator. <2 is excellent, >5 indicates problems. |
| **Efficiency Score** | Throughput ÷ Resource Usage | How well resources are utilized. |
| **Throughput Score** | (Test ÷ Max Observed) × 100 | Normalized throughput (0-100). |
| **Latency Score** | 100 - ((Test ÷ Max Observed) × 100) | Normalized latency (0-100, higher=better). |

---

## Excel Report Sheets

### Sheet 1: Dashboard

**Purpose:** Executive summary with key findings at a glance.

**Contents:**
- **KPI Boxes:** Peak throughput, lowest latency, best configuration
- **Top 5 Configurations:** Ranked by balanced score
- **4 Summary Charts:** Throughput overview, latency distribution, knee preview, scaling summary

**How to Use:** Start here to understand overall performance. The "Best Configuration" shows optimal settings for your workload.

---

### Sheet 2: Throughput Analysis

**Purpose:** Deep dive into throughput performance across all configurations.

**Charts:**
1. **Throughput by Acks Setting** - Compare acks=0, acks=1, acks=all
2. **Throughput by Batch Size** - Impact of batching on performance
3. **Records/sec vs MB/sec Correlation** - Validate message size impact
4. **Compression Efficiency** - Compare compression algorithms

**Key Insights:**
- acks=0 typically yields 2-3x higher throughput than acks=all
- Larger batch sizes improve throughput up to a point
- Compression trades CPU for network bandwidth

---

### Sheet 3: Latency Analysis

**Purpose:** Understand latency characteristics and percentile distributions.

**Charts:**
1. **Latency by Acks Setting** - Durability vs speed trade-off
2. **Latency Distribution (Percentiles)** - P50, P95, P99, P99.9 comparison
3. **Latency Heatmap** - Multi-dimensional view by batch/linger
4. **Latency vs Throughput** - The fundamental trade-off

**Key Insights:**
- P99 latency is typically 2-5x the average
- Batching increases latency but improves throughput
- Look for configurations where P99/Avg ratio is low (consistent performance)

---

### Sheet 4: Trade-off Analysis (THE KNEE CHART)

**Purpose:** The most critical visualization showing the latency-throughput saturation curve.

**The Knee Chart Explained:**

```
Latency
(ms)
  ^
  |                    * * *
  |                  *       SATURATION ZONE
  |                *         (Avoid this area)
  |             *
  |          *  <- THE KNEE (optimal operating point)
  |        *
  |      *      DIMINISHING RETURNS
  |    *        (Be careful here)
  |  *
  | *   SAFE ZONE
  |*    (Good performance)
  +-------------------------> Throughput (MB/s)
```

**What the Knee Shows:**
- **Safe Zone:** Low throughput, low latency. System underutilized.
- **Knee Point:** Optimal balance. Maximum throughput before latency spikes.
- **Diminishing Returns:** Throughput gains cause disproportionate latency increases.
- **Saturation Zone:** System overloaded. Avoid operating here.

**How to Find Your Optimal Configuration:**
1. Look for the "knee" where the curve bends upward
2. Choose configurations just before this point
3. The polynomial trendline helps visualize the curve

---

### Sheet 5: Scaling Performance

**Purpose:** Analyze how performance degrades with multiple producers/consumers.

**Charts:**
1. **Throughput Scaling** - Total throughput vs producer count
2. **Per-Producer Efficiency** - Throughput per producer as count increases
3. **Latency Degradation** - How latency increases with load
4. **Scaling Efficiency Curve** - Percentage of ideal linear scaling

**Key Insights:**
- Ideal: Linear scaling (2 producers = 2x throughput)
- Reality: Diminishing returns due to contention
- Sweet spot: Usually 3-5 producers per partition

**Example Interpretation:**
```
Producers | Total MB/s | Per-Producer | Efficiency
    1     |    100     |     100      |   100%
    3     |    270     |      90      |    90%
    5     |    400     |      80      |    80%
   10     |    600     |      60      |    60%  <- Contention significant
```

---

### Sheet 6: Configuration Heatmap

**Purpose:** Multi-dimensional parameter analysis using color-coded cells.

**Heatmap Interpretation:**
- **Green:** High performance (good)
- **Yellow:** Medium performance (acceptable)
- **Red:** Low performance (avoid)

**Dimensions Analyzed:**
- Batch Size vs Linger Time
- Acks Setting vs Compression Type
- Message Size vs Throughput

**How to Use:**
1. Find green cells - these are optimal parameter combinations
2. Avoid red cells - these configurations underperform
3. Look for patterns - e.g., "larger batch + higher linger = better throughput"

---

### Sheet 7: Message Size Impact

**Purpose:** Understand how message size affects throughput and efficiency.

**Charts:**
1. **Throughput vs Message Size** - MB/sec across different sizes
2. **Records/sec vs Message Size** - Message rate (inverse relationship)
3. **Efficiency Curve** - Bytes processed per unit overhead

**Key Insights:**
- Larger messages = higher MB/s throughput
- Larger messages = lower messages/sec
- Sweet spot typically 1KB-4KB for most workloads
- Very small messages (<256 bytes) have high overhead

**Example Pattern:**
```
Size (bytes) | MB/s  | msgs/sec | Overhead
    128      |  15   | 120,000  | High (metadata dominant)
    512      |  45   | 90,000   | Moderate
   1024      |  80   | 80,000   | Balanced
   4096      | 150   | 37,500   | Low
  16384      | 200   | 12,500   | Very low (bulk transfer)
```

---

### Sheet 8: Acks Comparison

**Purpose:** Quantify the durability vs performance trade-off.

**Acks Settings Explained:**

| Setting | Behavior | Durability | Performance |
|---------|----------|------------|-------------|
| `acks=0` | Fire and forget. No acknowledgment. | None | Fastest |
| `acks=1` | Leader acknowledges. | Moderate | Balanced |
| `acks=all` | All in-sync replicas acknowledge. | Highest | Slowest |

**Charts:**
1. **Throughput Comparison** - Side-by-side acks comparison
2. **Latency Comparison** - Impact on response time
3. **Trade-off Visualization** - Cost of durability

**Typical Results:**
```
acks=0:   ~150 MB/s, ~5ms avg latency   (no guarantees)
acks=1:   ~100 MB/s, ~15ms avg latency  (leader durable)
acks=all: ~60 MB/s,  ~30ms avg latency  (fully durable)
```

**When to Use Each:**
- **acks=0:** Metrics, logs, data you can afford to lose
- **acks=1:** Most production workloads (good balance)
- **acks=all:** Financial transactions, critical data

---

### Sheet 9: Raw Data

**Purpose:** Complete dataset for custom analysis and pivot tables.

**Columns Include:**
- All test parameters (acks, batch_size, linger_ms, compression, message_size)
- All metrics (throughput, latency percentiles)
- Calculated scores
- Test metadata (timestamp, scenario)

**How to Use:**
1. Create pivot tables for custom analysis
2. Filter by specific parameters
3. Export for external tools (Grafana, etc.)
4. Validate report calculations

---

### Sheet 10: Recommendations

**Purpose:** Actionable configuration recommendations for different use cases.

**Use Case Profiles:**

| Profile | Priority | Best For |
|---------|----------|----------|
| **Max Throughput** | Throughput > Latency | Batch processing, ETL, log aggregation |
| **Balanced** | Throughput ≈ Latency | General production workloads |
| **Low Latency** | Latency > Throughput | Real-time applications, trading |
| **Durability** | Safety > Performance | Financial, compliance workloads |

**Score Calculation:**
```
Max Throughput Score = (Throughput × 0.7) + (Latency × 0.2) + (Consistency × 0.1)
Balanced Score       = (Throughput × 0.4) + (Latency × 0.4) + (Consistency × 0.2)
Low Latency Score    = (Throughput × 0.2) + (Latency × 0.6) + (Consistency × 0.2)
Durability Score     = Based on acks=all configurations only
```

---

## Scoring Methodology

### How Scores Are Calculated

**1. Throughput Score (0-100):**
```
Score = (config_throughput / max_observed_throughput) × 100
```
Higher throughput = higher score.

**2. Latency Score (0-100):**
```
Score = 100 - ((config_latency / max_observed_latency) × 100)
```
Lower latency = higher score (inverted).

**3. Consistency Score (0-100):**
```
Ratio = P99_latency / Avg_latency
Score = 100 - ((Ratio - 1) × 20)  # Capped at 0-100
```
Lower P99/Avg ratio = higher score.

**4. Weighted Scores:**
Each use case applies different weights to create a composite score.

---

## Configuration Parameters

### Producer Parameters

| Parameter | Default | Range | Impact |
|-----------|---------|-------|--------|
| `acks` | 1 | 0, 1, all | Durability vs throughput |
| `batch.size` | 16384 | 1024-1048576 | Batching efficiency |
| `linger.ms` | 0 | 0-1000 | Wait time to fill batches |
| `compression.type` | none | none, snappy, lz4, zstd | CPU vs bandwidth |
| `buffer.memory` | 32MB | 32MB-256MB | Producer buffer size |
| `max.in.flight.requests` | 5 | 1-10 | Parallelism (affects ordering) |

### Consumer Parameters

| Parameter | Default | Range | Impact |
|-----------|---------|-------|--------|
| `fetch.min.bytes` | 1 | 1-10MB | Minimum fetch size |
| `fetch.max.wait.ms` | 500 | 0-10000 | Max wait for fetch.min.bytes |
| `max.poll.records` | 500 | 1-10000 | Records per poll() |
| `receive.buffer.bytes` | 64KB | 32KB-64MB | Socket buffer |

---

## Interpreting Results

### Good vs Bad Results

**Healthy Performance Indicators:**
- P99/Avg latency ratio < 3
- Throughput within 20% of theoretical max
- Linear scaling up to partition count
- No outlier latencies (P99.9 within 2x of P99)

**Warning Signs:**
- P99/Avg ratio > 5 (inconsistent performance)
- Throughput drops significantly with acks=1 vs acks=0
- Scaling efficiency < 50% with multiple producers
- Max latency > 10x average

### Common Patterns

**Pattern 1: High Throughput, High Latency Variance**
- Cause: Large batches, high linger.ms
- Solution: Reduce batch size or linger.ms for more consistent latency

**Pattern 2: Low Throughput Despite Good Configuration**
- Cause: Network bottleneck, disk I/O, or broker overload
- Solution: Check broker metrics, increase partitions

**Pattern 3: Degraded Scaling**
- Cause: Too many producers for partition count
- Solution: Increase partitions or reduce producer count

**Pattern 4: Compression Not Helping**
- Cause: Already compressible data or CPU bottleneck
- Solution: Try different algorithm or disable compression

### Making Decisions

**Step 1:** Determine your priority (throughput vs latency vs durability)

**Step 2:** Check the Recommendations sheet for your use case

**Step 3:** Validate on the Trade-off Analysis (Knee Chart)
- Is the recommended config before the knee? Good.
- Is it in the saturation zone? Choose a more conservative setting.

**Step 4:** Review Raw Data for edge cases
- Check max latency for SLA compliance
- Verify P99.9 is acceptable

**Step 5:** Test in production with monitoring
- Start conservative, gradually optimize
- Monitor actual latency distributions

---

## Quick Reference Card

### Optimal Starting Points

| Workload | acks | batch.size | linger.ms | compression |
|----------|------|------------|-----------|-------------|
| **Logs/Metrics** | 0 | 65536 | 20 | lz4 |
| **Events** | 1 | 32768 | 10 | zstd |
| **Transactions** | all | 16384 | 5 | none |
| **Bulk ETL** | 1 | 131072 | 50 | zstd |

### Red Flags to Watch

- Max latency > 10 seconds
- P99 > 5x average
- Throughput < 10 MB/s (for modern hardware)
- Scaling efficiency < 30%

### Target Benchmarks (Modern Hardware)

| Metric | Good | Excellent |
|--------|------|-----------|
| Throughput | >50 MB/s | >100 MB/s |
| Avg Latency | <50ms | <10ms |
| P99 Latency | <200ms | <50ms |
| Scaling Efficiency | >60% | >80% |
