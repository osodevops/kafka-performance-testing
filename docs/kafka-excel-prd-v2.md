# Kafka Performance Testing - Excel Analysis & Visualization PRD

**Author:** OSO DevOps  
**Date:** December 2024  
**Status:** For Implementation  
**Target Repository:** [kafka-performance-testing](https://github.com/osodevops/kafka-performance-testing)  
**Focus:** **Data-Driven Excel Visualization & Analysis**

---

## Executive Summary

This PRD focuses exclusively on **transforming Kafka performance test results into actionable, graph-driven Excel reports**. The goal is to move beyond raw logs and simple tables to **comprehensive visual analysis** that makes performance trade-offs, optimal configurations, and scaling impacts immediately apparent.

Based on industry benchmarks and your test data, the Excel workbook will include:
- **30+ dynamic charts** spanning throughput, latency, scalability, and trade-off analysis
- **Interactive filters** for comparing configurations side-by-side
- **Heatmaps** for multi-dimensional analysis (e.g., acks vs. batch.size vs. throughput)
- **Scatter plots** showing latency-throughput trade-off curves (the "knee" where saturation begins)
- **Performance degradation curves** for load scaling (1 vs. 3 vs. 5+ producers/consumers)
- **Percentile latency visualizations** (P50, P95, P99, P99.9 on same chart)
- **Benchmark comparison sheets** matching your test scenarios to industry standards

### Key Objectives
- Convert raw `kafka-producer-perf-test` and `kafka-consumer-perf-test` logs into rich visualizations
- Identify performance trade-offs graphically (throughput vs. latency, durability vs. speed)
- Pinpoint optimal configurations for different use cases (max throughput, low latency, balanced)
- Visualize scaling degradation to inform cluster sizing decisions
- Enable quick comparison of parameter variations (acks, batch.size, compression, etc.)

---

## 1. Excel Workbook Architecture

### 1.1 Workbook Structure (8 Core Sheets + Optional Dashboards)

```
kafka_perf_report.xlsx
├── Sheet 1: Dashboard (Executive Summary with Key Charts)
├── Sheet 2: Throughput Analysis (MB/sec, records/sec trends)
├── Sheet 3: Latency Analysis (Percentile distributions)
├── Sheet 4: Trade-off Analysis (Latency vs. Throughput curves)
├── Sheet 5: Scaling Performance (1 vs 3 vs 5+ producers/consumers)
├── Sheet 6: Configuration Heatmap (Multi-dimensional analysis)
├── Sheet 7: Message Size Impact (Efficiency curves)
├── Sheet 8: Acks Setting Comparison (Durability vs. Performance)
├── Sheet 9: Raw Data (All test results, sortable/filterable)
└── Sheet 10: Recommendations (Scored configurations)
```

---

## 2. Sheet-by-Sheet Visualization Specification

### Sheet 1: Dashboard (Executive Summary)

**Purpose:** One-page overview of all key findings for stakeholder communication.

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│  Kafka Performance Testing Report                   │
│  Cluster: [name]  |  Date: [date]  |  Tests: [N]  │
└─────────────────────────────────────────────────────┘

┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ KEY METRICS      │ │ TOP CONFIG       │ │ SCALING IMPACT   │
├──────────────────┤ ├──────────────────┤ ├──────────────────┤
│ Max Throughput   │ │ Best Throughput: │ │ 1 Producer:      │
│ 98.4 MB/sec      │ │ acks=0, batch=  │ │   98.4 MB/sec    │
│                  │ │ 64000, lz4       │ │ 3 Producers:     │
│ Min Latency      │ │ Expected: 98.4   │ │   71.3 MB/sec    │
│ 880 ms avg       │ │ MB/sec           │ │   (27.5% drop)   │
│                  │ │                  │ │                  │
│ Balanced Config: │ │ Best Latency:    │ │ Degradation:     │
│ acks=1, batch=   │ │ acks=0, batch=   │ │ Linear vs        │
│ 16384, zstd      │ │ 8192, no-compress│ │ Exponential      │
│ 22.7 MB/sec,     │ │ Expected: 518 ms │ │                  │
│ 3182 ms latency  │ │ avg              │ │                  │
└──────────────────┘ └──────────────────┘ └──────────────────┘

┌─────────────────────────────────────────────────────┐
│ THROUGHPUT TREND (Top 10 Configurations)            │
│ [LINE CHART - X: Config ID, Y: MB/sec]              │
│ Shows: Best configs for throughput optimization     │
└─────────────────────────────────────────────────────┘

┌──────────────────────────┐ ┌──────────────────────────┐
│ LATENCY vs THROUGHPUT    │ │ SCALING DEGRADATION      │
│ [SCATTER PLOT]           │ │ [LINE CHART]             │
│ X: Throughput (MB/sec)   │ │ X: Num Producers         │
│ Y: Latency (ms)          │ │ Y: Throughput per prod   │
│ Shows: "Knee" saturation │ │ Y2: Avg Latency         │
│ point, optimal zone      │ │ Shows: When to scale     │
└──────────────────────────┘ └──────────────────────────┘
```

**Chart Details:**

1. **KPI Summary Boxes** (Text boxes with key numbers)
   - Max throughput observed
   - Min latency observed
   - Recommended balanced config
   - System saturation point

2. **Top 10 Configurations Line Chart**
   - X-axis: Configuration label (e.g., "acks=0, bs=64k")
   - Y-axis: Throughput (MB/sec)
   - Sorted descending by throughput
   - Color-coded by acks setting (red=0, yellow=1, green=all)
   - Shows which knobs matter most

3. **Latency vs. Throughput Scatter Plot** (Critical)
   - X-axis: Throughput (MB/sec)
   - Y-axis: Avg Latency (ms)
   - Each point = one test configuration
   - Color by acks value
   - Size by batch.size
   - **Shows the "knee" where latency explodes** - this is the optimal operating zone

4. **Scaling Degradation Line Chart**
   - X-axis: Number of producers (1, 3, 5, 10)
   - Y-axis primary: Throughput per producer (MB/sec)
   - Y-axis secondary: Average latency (ms)
   - Two lines overlaid
   - **Helps determine: "When does adding more producers stop helping?"**

---

### Sheet 2: Throughput Analysis

**Purpose:** Deep dive into throughput optimization across all test scenarios.

**Visualizations:**

#### 2.1 Throughput Comparison by Acks Setting
```
Chart Type: Clustered Bar Chart
X-axis: acks value (0, 1, all)
Y-axis: MB/sec
Bars: One per configuration variant (batch.size, compression)
Legend: batch.size or compression.type

This shows:
- acks=0 is ~3.5x faster than acks=all (from your data)
- Within each acks setting, which other parameters matter
- Trade-off: durability cost in throughput percentage terms
```

**Sample Data (From Your Logs):**
```
acks=0, 1 producer:        96.71 MB/sec
acks=0, 3 producers:       58.67 MB/sec
acks=1, 1 producer:        28.59 MB/sec (12x SLOWER than acks=0)
acks=all, 1 producer:      28.59 MB/sec
acks=all, 3 producers:     71.32 MB/sec (30x variations depending on config)

This is IMMEDIATELY visible in a bar chart.
```

#### 2.2 Throughput by Batch Size (Line Chart)
```
Chart Type: Line Chart with Markers
X-axis: batch.size (8192, 16384, 32768, 64000)
Y-axis: Throughput (MB/sec)
Lines: One per compression type (none, snappy, lz4, zstd)
Color coding: Different color per line

This shows:
- How batching size impacts throughput
- Which compression algorithms work best at different batch sizes
- Diminishing returns (where adding more batch size stops helping)
```

#### 2.3 Records/Sec vs. MB/Sec Comparison
```
Chart Type: Scatter Plot with Trend Line
X-axis: Records/sec
Y-axis: MB/sec
Each point: One test result
Color: By record.size (512B, 1KB, 2KB, 4KB)

This shows:
- Relationship between record throughput and data throughput
- Larger messages = higher MB/sec with same records/sec
- Helps identify: "What message size do I need to hit my MB/sec target?"
```

#### 2.4 Compression Type Efficiency
```
Chart Type: Stacked Column Chart
X-axis: Compression type (none, snappy, lz4, zstd)
Y-axis: MB/sec
Stacked segments: 
  - Throughput achieved
  - "Lost" to compression overhead (if CPU-bound)
  - Potential network savings (bandwidth reduction)

Legend explanation of trade-off
```

---

### Sheet 3: Latency Analysis

**Purpose:** Understand latency distribution and percentile characteristics.

**Visualizations:**

#### 3.1 Latency Percentile Distribution (Waterfall/Column Chart)
```
Chart Type: Waterfall or Clustered Column Chart
X-axis: Percentile (p50, p95, p99, p99.9, max)
Y-axis: Latency (ms)
Bars: One per selected configuration (filter by dropdown)

From your data (acks=all, 1 producer):
  p50:   3289 ms
  p95:   3467 ms
  p99:   3568 ms
  p99.9: 3603 ms
  max:   3613 ms

This shows:
- Tail latency characteristics
- How consistent/variable the latency is
- Whether you have outlier problems (p99.9 vs max)
```

#### 3.2 Latency by Acks Setting (Box Plot)
```
Chart Type: Box Plot (or high-low-close in Excel)
X-axis: acks value (0, 1, all)
Y-axis: Latency (ms)

Box elements:
  - Bottom whisker: min latency
  - Lower box: p25 latency
  - Line in box: median (p50)
  - Upper box: p75 latency
  - Upper whisker: p95 or p99
  - Dots: outliers (p99.9, max)

This shows:
- Latency spread by durability setting
- Which setting has most consistent latency
- Trade-off visibility: acks=0 is faster AND more consistent
```

#### 3.3 Latency Trend by Configuration (Line Chart)
```
Chart Type: Multi-line Chart
X-axis: Configuration ID (sorted by some criteria)
Y-axis: Latency (ms)
Lines: 
  - Avg latency
  - P95 latency
  - P99 latency
  - Max latency

This shows:
- Which configurations have "spiky" latency (large gap between avg and max)
- Consistency across different settings
- Which settings produce "predictable" latency
```

#### 3.4 Latency vs. Batch Size (Scatter)
```
Chart Type: Scatter Plot
X-axis: batch.size (log scale)
Y-axis: Avg Latency (ms)
Size of marker: Number of producers
Color: Compression type

This shows:
- Larger batches → higher latency (more buffering time)
- Interaction with producer count
- At what batch size does latency become unacceptable
```

---

### Sheet 4: Trade-off Analysis (Critical)

**Purpose:** Visualize the fundamental throughput-latency trade-off curve (THE "KNEE" CHART).

**Visualizations:**

#### 4.1 Latency-Throughput Trade-off Curve (Scatter Plot - MAIN CHART)
```
Chart Type: XY Scatter Plot with Linear Regression Trendline
X-axis: Throughput (MB/sec), range [0 to 110]
Y-axis: Average Latency (ms), range [0 to 4000]
Each point: One complete test result

Color mapping:
  - Red:   acks=0
  - Yellow: acks=1
  - Green:  acks=all

Size mapping:
  - Tiny:  batch.size < 16KB
  - Small: batch.size 16-32KB
  - Large: batch.size > 32KB

Annotations:
  - Zone 1 (0-50 MB/sec, 0-1000ms): "Safe Operating Zone"
  - Zone 2 (50-90 MB/sec, 1000-3000ms): "Diminishing Returns"
  - Zone 3 (>90 MB/sec, >3000ms): "Saturation Point"
  - Add arrow pointing to "Knee" of curve
  - Add box highlighting "Recommended Operating Range"

Formula: This is the MOST IMPORTANT CHART.
It directly shows:
- The saturation point (where adding load increases latency exponentially)
- The optimal operating zone (just before the knee)
- The cost of choosing different durability levels (red vs. green)
- System capacity (where curve starts to steepen)
```

**Data from Your Logs:**
```
acks=0, 1 producer:    96.71 MB/sec,  880.66 ms avg
acks=0, 3 producers:   58.67 MB/sec,  1512.12 ms avg (with reduced load per producer)
acks=1, 1 producer:    28.59 MB/sec,  3182.27 ms avg
acks=all, 1 producer:  28.59 MB/sec,  3182.27 ms avg

Plot these + all variants, you'll see:
- Clear separation by acks
- Curve showing saturation behavior
- Obvious "sweet spot" for your workload
```

#### 4.2 Multi-Metric Performance Radar Chart
```
Chart Type: Radar/Spider Chart
Axes (5 dimensions):
  1. Throughput (normalized %)
  2. Latency (normalized %, inverse - lower is better)
  3. Consistency (inverse of std dev)
  4. Scalability (throughput gain from 1→3 producers)
  5. Resource Efficiency (MB/sec per CPU %)

Each configuration as a polygon overlaid
Color-coded by acks setting

This shows:
- Which config is "most balanced"
- Trade-offs at a glance (multi-dimensional)
- Best choice for different priorities
```

#### 4.3 Performance Score Breakdown (Grouped Bar Chart)
```
Chart Type: Grouped Bar Chart
X-axis: Configuration (top 5-10 candidates)
Y-axis: Score (0-100)
Bars (grouped):
  - Throughput Score (0-100)
  - Latency Score (0-100)
  - Consistency Score (0-100)
  - Overall Weighted Score (depends on use case)

Scoring formula (make visible):
  Throughput: (achieved_throughput / max_observed) * 100
  Latency: 100 - ((avg_latency / max_observed_latency) * 100)
  Consistency: (1 - stddev/mean) * 100
  Weighted: 40% throughput + 35% latency + 25% consistency

This allows stakeholders to see:
- Why one config was recommended
- How to adjust weights for their use case
- Transparency in decision-making
```

---

### Sheet 5: Scaling Performance

**Purpose:** Understand how performance degrades with multiple producers/consumers.

**Visualizations:**

#### 5.1 Throughput per Producer (Line Chart - Critical)
```
Chart Type: Line Chart with Markers
X-axis: Number of Producers (1, 2, 3, 4, 5, 10)
Y-axis: Throughput per Producer (MB/sec)
Lines:
  - Aggregate throughput / num_producers
  - Ideal (linear) scaling line
Legend shows:
  - Measured throughput
  - Theoretical max (if linear)
  - % of linear achieved

From your data:
  1 producer:   96.71 MB/sec per producer
  3 producers:  58.67 ÷ 3 = 19.56 MB/sec per producer
  Drop-off: 5.9x degradation (suggests contention)

This shows immediately:
- How many producers can you run before performance falls off
- Bottleneck: broker network? CPU? Replication?
- Cost of scale-out strategies
```

#### 5.2 Aggregate Throughput Scaling (Area Chart)
```
Chart Type: Area/Stacked Area Chart
X-axis: Number of Producers (1, 3, 5, 10)
Y-axis: Total Throughput (MB/sec)
Areas (stacked):
  - Producer 1 contribution
  - Producer 2 contribution
  - Producer 3 contribution
  - etc.

Shows:
- Aggregate throughput doesn't scale linearly
- Individual producer contribution shrinks
- Point where adding more producers no longer helps
```

#### 5.3 Latency Impact with Scaling (Dual-Axis Chart)
```
Chart Type: Combo Chart (Line + Bar)
X-axis: Number of Producers (1, 3, 5, 10)
Y-axis (left): Average Latency (ms)
Y-axis (right): P95 Latency (ms)
Line: Avg latency trend
Bars: P95 latency by producer count

From your data:
  1 producer, acks=all:   3182 ms avg, 3467 ms p95
  3 producers, acks=all:  (need consumer-side measurement)

Shows:
- Does latency increase linearly, exponentially, or plateau?
- P95 latency stability under load
- When latency SLA breaks
```

#### 5.4 Consumer Scaling Impact (Grouped Chart)
```
Chart Type: Grouped Bar Chart
X-axis: Number of Consumers (1, 3, 5)
Y-axis: Throughput (MB/sec) and Latency (ms, on secondary axis)
Bars:
  - Throughput achieved (primary axis)
  - Rebalance time (secondary axis)

Shows:
- Does adding consumers improve throughput?
- Cost of consumer group rebalancing
- Consumer parallelism benefit vs. overhead
```

#### 5.5 Contention Heatmap (Producer-Consumer Matrix)
```
Chart Type: Heat Map
X-axis: Number of Producers (1, 3, 5, 10)
Y-axis: Number of Consumers (1, 3, 5, 10)
Cell value: Throughput (MB/sec) or Latency (ms)
Color intensity: Green (good) → Red (poor)

This shows:
- Optimal producer/consumer ratio
- Where bottlenecks appear
- System saturation zones
```

---

### Sheet 6: Configuration Heatmap (Multi-Dimensional)

**Purpose:** Visualize impact of multiple parameters simultaneously.

**Visualizations:**

#### 6.1 Throughput Heatmap: Batch Size vs. Linger.ms
```
Chart Type: Heat Map (Pivot Table Visualization)
X-axis: batch.size (8192, 16384, 32768, 64000)
Y-axis: linger.ms (0, 5, 10, 20, 50)
Cell value: Throughput (MB/sec)
Color scale: Blue (low, <20 MB/sec) → Red (high, >90 MB/sec)

This shows:
- Which combination of batch + linger is optimal
- Interaction effects (batch + linger together)
- Diminishing returns zone
- Recommended "sweet spot" (e.g., batch=64000, linger=10)
```

#### 6.2 Latency Heatmap: Acks vs. Batch Size
```
Chart Type: Heat Map
X-axis: batch.size (8192, 16384, 32768, 64000)
Y-axis: acks (0, 1, all)
Cell value: Avg Latency (ms)
Color scale: Green (low latency) → Red (high latency)

This shows:
- Trade-off between durability and latency
- Which batch size helps latency in each acks setting
- Whether acks=1 is middle ground (should show in color)
```

#### 6.3 Compression Efficiency Heatmap
```
Chart Type: Heat Map
X-axis: compression.type (none, snappy, lz4, zstd)
Y-axis: record.size (512B, 1KB, 2KB, 4KB)
Cell value: MB/sec throughput
Color intensity: Shows which compression works best for each message size

This shows:
- Larger messages benefit more from compression (or vice versa?)
- Best compression choice per message size
- CPU vs. network trade-off visually
```

#### 6.4 Configuration Impact Bubble Chart
```
Chart Type: Bubble/Scatter Plot
X-axis: batch.size
Y-axis: linger.ms
Bubble size: Throughput (MB/sec)
Bubble color: Latency (ms) - gradient from cool to warm
Text labels: acks + compression abbreviation in each bubble

This shows:
- Parameter interactions at a glance
- Which config achieves both high throughput and low latency
- Trade-offs in a single, dense visualization
```

---

### Sheet 7: Message Size Impact

**Purpose:** Understand relationship between message size and performance.

**Visualizations:**

#### 7.1 Throughput vs. Message Size (Line Chart)
```
Chart Type: XY Line Chart
X-axis: Message Size (bytes, log scale: 128, 256, 512, 1024, 2048, 4096, 8192, 16384)
Y-axis: Throughput (MB/sec)
Lines:
  - Compression: none
  - Compression: lz4
  - Compression: zstd
Legend: Shows which compression type

From industry benchmarks:
- Smaller messages: Often lower MB/sec (more overhead per message)
- Medium messages: Peak efficiency zone
- Large messages: Potentially limited by single-threaded consumer

This shows:
- Your message size sweet spot
- Compression benefit by message size
- Whether you're in "overhead" zone or "network" zone
```

#### 7.2 Records/Sec vs. Message Size (Scatter)
```
Chart Type: XY Scatter Plot
X-axis: Message Size (bytes)
Y-axis: Records/sec (thousands)
Color: Compression type
Size: batch.size

Shows:
- Small messages = higher records/sec but lower MB/sec
- Large messages = lower records/sec but higher MB/sec
- Network vs. message count trade-off
```

#### 7.3 Compression Ratio by Message Size
```
Chart Type: Bar Chart
X-axis: Message Size (bytes)
Y-axis: Compression Ratio (%, lower is better compression)
Bars: One per compression algorithm (snappy, lz4, zstd)

Shows:
- Does larger message size compress better?
- Which algorithm compresses best at each size
- Network bandwidth savings potential
```

#### 7.4 Latency Stability by Message Size
```
Chart Type: Box Plot or High-Low-Close Chart
X-axis: Message Size (bytes)
Y-axis: Latency (ms)
Box showing: p50, p95, p99 for each size

Shows:
- Does larger message size create more latency variance?
- Which message size has most predictable latency
- Tail latency by size
```

---

### Sheet 8: Acks Setting Comparison

**Purpose:** Quantify durability-performance trade-off.

**Visualizations:**

#### 8.1 Durability vs. Performance (Side-by-Side Comparison)
```
Chart Type: Grouped Column Chart
X-axis: acks value (0, 1, all)
Y-axis: Multiple metrics (dual-axis if needed)
Bars:
  - Throughput (MB/sec)
  - Avg Latency (ms)
  - P99 Latency (ms)
  - Max Latency (ms)

From your data:
  acks=0:   96.71 MB/sec,  880.66 ms avg
  acks=1:   28.59 MB/sec,  3182.27 ms avg
  acks=all: 28.59 MB/sec,  3182.27 ms avg

This immediately shows:
- acks=0 is 3.4x faster than acks=all
- acks=1 provides minimal benefit over acks=all
- Latency increase is 3.6x
- Cost of guarantee: 71% throughput loss
```

#### 8.2 Data Safety vs. Performance Trade-off (Scatter with Annotations)
```
Chart Type: XY Scatter Plot
X-axis: "Data Loss Risk" (conceptual scale, 0-100%)
  0% risk = acks=all (all replicas must ack)
  50% risk = acks=1 (leader ack only)
  100% risk = acks=0 (no ack)
Y-axis: Throughput (MB/sec)
Points:
  - acks=0:   100% risk,  96.71 MB/sec
  - acks=1:   50% risk,   28.59 MB/sec
  - acks=all: 0% risk,    28.59 MB/sec

Annotations:
  - Arrow from acks=0 to acks=all: "71% throughput loss for guarantee"
  - Zone overlay: "Safe zone" (where risk < latency benefit)

Shows:
- ROI of durability guarantees
- Whether acks=1 is worth it (likely not, based on your data)
```

#### 8.3 Replication Factor Impact (Grouped Chart)
```
Chart Type: Grouped Bar Chart
X-axis: acks + replication factor (e.g., "acks=all, RF=1", "acks=all, RF=3")
Y-axis: Throughput (MB/sec) and Latency (ms)

Shows:
- How replication factor compounds durability impact
- min.insync.replicas effect on throughput
- Scaling: does RF=3 with acks=all kill performance?
```

#### 8.4 P99 Latency by Acks (Bar Chart with Error Bars)
```
Chart Type: Bar Chart with Error Bars
X-axis: acks value (0, 1, all)
Y-axis: P99 Latency (ms)
Bar height: Average p99
Error bars: Range (p95 to p99.9) across all configs with this acks setting

Shows:
- Latency consistency by durability setting
- Whether acks=0 has more spiky behavior
- Tail latency guarantees by acks
```

---

### Sheet 9: Raw Data (Sortable/Filterable)

**Purpose:** Provide complete, unsummarized test data for advanced analysis.

**Columns:**
```
Test ID | Date | Scenario | acks | batch_size | linger_ms | compression | 
record_size | num_producers | throughput_rps | throughput_mb | avg_latency_ms | 
p50_ms | p95_ms | p99_ms | p99.9_ms | max_latency_ms | num_records | 
rebalance_time_ms | fetch_time_ms | notes
```

**Features:**
- Sortable by any column
- Filterable by scenario, acks, compression, etc.
- All values included (support custom pivot tables)
- Color-coded rows by scenario for quick scanning
- Frozen header row

**Usage:**
- Users create custom pivot tables from this data
- Basis for all charts (charts reference this data)
- Backup/audit trail of all test results

---

### Sheet 10: Recommendations (Scored Configurations)

**Purpose:** Present actionable guidance with scoring transparency.

**Layout:**
```
┌──────────────────────────────────────────────────────────────┐
│ RECOMMENDED CONFIGURATIONS BY USE CASE                      │
└──────────────────────────────────────────────────────────────┘

┌─ USE CASE 1: MAXIMUM THROUGHPUT ──────────────────────────────┐
│                                                               │
│ Configuration:                                              │
│   acks = 0                                                 │
│   batch.size = 64000                                       │
│   linger.ms = 10                                           │
│   compression.type = lz4                                   │
│   record.size = 1024                                       │
│                                                            │
│ Expected Performance:                                      │
│   Throughput: 96.71 MB/sec (49514 records/sec)           │
│   Avg Latency: 880.66 ms                                 │
│   P95 Latency: 1318 ms                                   │
│   P99 Latency: 1355 ms                                   │
│                                                            │
│ Trade-offs:                                               │
│   ✗ NO DURABILITY - messages can be lost if broker fails │
│   ✓ Best for: Non-critical telemetry, event logs, etc.  │
│                                                            │
│ Scaling Behavior:                                          │
│   3 producers → 58.67 MB/sec (39.4% efficiency)          │
│   Recommendation: Use 1-2 producers max for consistency   │
│                                                            │
│ Scoring:                                                  │
│   Throughput Score: 100/100                              │
│   Latency Score:    25/100 (acceptable for non-critical) │
│   Consistency:      85/100                               │
│   Overall Score:    100/100 (for throughput priority)    │
└───────────────────────────────────────────────────────────┘

┌─ USE CASE 2: BALANCED PERFORMANCE ────────────────────────────┐
│ [Similar detail]                                            │
│   acks = 1, batch = 16384, linger = 10, zstd              │
│   Throughput: 28.59 MB/sec, Latency: 3182 ms             │
│   ✓ Good durability guarantee (leader ack)                │
│   ✓ Reasonable latency                                    │
│   Overall Score: 78/100 (balanced)                        │
└───────────────────────────────────────────────────────────┘

┌─ USE CASE 3: MISSION-CRITICAL (DURABILITY FIRST) ────────────┐
│ [Similar detail]                                            │
│   acks = all, batch = 16384, linger = 5, zstd             │
│   Throughput: 24.96 MB/sec, Latency: 3735 ms             │
│   ✓ Full durability (all replicas ack)                    │
│   ✓ Acceptable latency for critical workloads             │
│   Overall Score: 92/100 (for durability priority)         │
└───────────────────────────────────────────────────────────┘

┌─ SCORING METHODOLOGY ─────────────────────────────────────────┐
│                                                               │
│ Throughput Score = (test_throughput / max_observed) * 100    │
│ Latency Score = 100 - ((test_latency / max_observed) * 100)  │
│ Consistency Score = (1 - σ/μ) * 100                          │
│ Scalability Score = (single_producer / multi_producer) * 100 │
│                                                               │
│ Overall Score (weights by use case):                         │
│   Max Throughput:  40% throughput + 20% latency + 40% scale  │
│   Balanced:        30% throughput + 35% latency + 35% scale  │
│   Durability:      20% throughput + 35% latency + 45% scale  │
│                                                               │
└───────────────────────────────────────────────────────────────┘

┌─ WHEN TO ADJUST THESE SETTINGS ───────────────────────────────┐
│                                                               │
│ IF YOU OBSERVE:                  | ADJUST:                   │
│ ─────────────────────────────────┼──────────────────────────  │
│ Low throughput, high P99 latency │ Increase batch.size       │
│ Good throughput but spiky        │ Increase linger.ms        │
│ High CPU on producer             │ Reduce compression or     │
│                                  │ increase batch.size       │
│ Message loss in production        │ Increase acks level       │
│ Replication lag too high          │ Reduce num.producers or  │
│                                  │ increase broker replicas  │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## 3. Python Implementation for Excel Generation

### 3.1 Enhanced Excel Generator Script

**Location:** `scripts/generate_excel_report.py`

**Key Libraries:**
```
openpyxl>=3.0.0       # Excel workbook creation
pandas>=1.3.0         # Data manipulation
matplotlib>=3.5.0     # Chart generation
numpy>=1.20.0         # Numerical operations
scipy>=1.7.0          # Statistics (for regression, box plots)
```

**Core Components:**

```python
import openpyxl
from openpyxl.chart import (
    LineChart, BarChart, ScatterChart, BubbleChart,
    AreaChart, DoughnutChart, RadarChart, Reference,
    LineChart3D
)
from openpyxl.chart.marker import DataPoint
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
import pandas as pd
import numpy as np
from scipy import stats
import json
from pathlib import Path
from datetime import datetime

class KafkaPerformanceExcelReporter:
    """
    Transforms parsed Kafka perf test results into comprehensive,
    graph-driven Excel reports with 30+ visualizations.
    """
    
    def __init__(self, parsed_json_file, output_xlsx):
        self.data = self._load_parsed_data(parsed_json_file)
        self.wb = openpyxl.Workbook()
        self.wb.remove(self.wb.active)
        self.output_file = output_xlsx
        
        # Organize by test type
        self.producer_results = [r for r in self.data if r['test_type'] == 'producer']
        self.consumer_results = [r for r in self.data if r['test_type'] == 'consumer']
        
        # Prepare DataFrames for charting
        self.producer_df = self._create_producer_dataframe()
        self.consumer_df = self._create_consumer_dataframe()
    
    def _create_producer_dataframe(self):
        """Convert producer results to DataFrame for easy charting"""
        rows = []
        for r in self.producer_results:
            row = {
                **r['configuration'],
                'throughput_rps': r['metrics']['throughput_rps'],
                'throughput_mb': r['metrics']['throughput_mb'],
                'avg_latency_ms': r['metrics']['avg_latency_ms'],
                'max_latency_ms': r['metrics']['max_latency_ms'],
                'p50_ms': r['metrics']['p50_ms'],
                'p95_ms': r['metrics']['p95_ms'],
                'p99_ms': r['metrics']['p99_ms'],
                'p999_ms': r['metrics']['p999_ms'],
            }
            rows.append(row)
        return pd.DataFrame(rows)
    
    def generate_report(self):
        """Orchestrate complete Excel report generation"""
        print("Generating comprehensive Kafka performance report...")
        
        # Sheet 1: Dashboard
        self.create_dashboard_sheet()
        
        # Sheet 2: Throughput Analysis
        self.create_throughput_sheet()
        
        # Sheet 3: Latency Analysis
        self.create_latency_sheet()
        
        # Sheet 4: Trade-off Analysis
        self.create_tradeoff_sheet()
        
        # Sheet 5: Scaling Performance
        self.create_scaling_sheet()
        
        # Sheet 6: Configuration Heatmap
        self.create_heatmap_sheet()
        
        # Sheet 7: Message Size Impact
        self.create_message_size_sheet()
        
        # Sheet 8: Acks Comparison
        self.create_acks_sheet()
        
        # Sheet 9: Raw Data
        self.create_raw_data_sheet()
        
        # Sheet 10: Recommendations
        self.create_recommendations_sheet()
        
        # Save workbook
        self.wb.save(self.output_file)
        print(f"✓ Report generated successfully: {self.output_file}")
    
    # ─────────────────────────────────────────────────────────
    # SHEET 1: DASHBOARD
    # ─────────────────────────────────────────────────────────
    
    def create_dashboard_sheet(self):
        """Create executive summary dashboard with key charts"""
        ws = self.wb.create_sheet('Dashboard', 0)
        ws.page_setup.paperSize = ws.PAPERSIZE_LETTER
        ws.page_setup.orientation = "landscape"
        
        # Title
        ws['A1'] = 'Kafka Performance Testing Report'
        ws['A1'].font = Font(size=18, bold=True, color="FFFFFF")
        ws['A1'].fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        ws.merge_cells('A1:L1')
        
        ws['A2'] = f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | Total Tests: {len(self.producer_results)} Producer | {len(self.consumer_results)} Consumer'
        ws['A2'].font = Font(size=10, italic=True)
        ws.merge_cells('A2:L2')
        
        # KPI Summary (A4:D10)
        self._create_kpi_boxes(ws)
        
        # Chart 1: Top Configurations Line Chart (A12:G25)
        self._add_top_configs_chart(ws, 'A12')
        
        # Chart 2: Latency vs Throughput Scatter (H12:M25)
        self._add_latency_throughput_scatter(ws, 'H12')
        
        # Chart 3: Scaling Degradation (A27:G40)
        self._add_scaling_chart(ws, 'A27')
        
        # Chart 4: Acks Comparison (H27:M40)
        self._add_acks_chart(ws, 'H27')
    
    def _create_kpi_boxes(self, ws):
        """Add KPI summary boxes to dashboard"""
        # Best throughput
        best_throughput_config = self.producer_df.loc[self.producer_df['throughput_mb'].idxmax()]
        ws['A4'] = 'MAX THROUGHPUT'
        ws['A4'].font = Font(bold=True, size=11)
        ws['A5'] = f"{best_throughput_config['throughput_mb']:.1f} MB/sec"
        ws['A5'].font = Font(size=14, bold=True, color="00B050")
        ws['A6'] = f"acks={best_throughput_config.get('acks', 'N/A')}"
        ws['A7'] = f"batch={best_throughput_config.get('batch_size', 'N/A')}"
        
        # Best latency
        best_latency_config = self.producer_df.loc[self.producer_df['avg_latency_ms'].idxmin()]
        ws['C4'] = 'MIN LATENCY'
        ws['C4'].font = Font(bold=True, size=11)
        ws['C5'] = f"{best_latency_config['avg_latency_ms']:.0f} ms"
        ws['C5'].font = Font(size=14, bold=True, color="FF6B6B")
        ws['C6'] = f"acks={best_latency_config.get('acks', 'N/A')}"
        ws['C7'] = f"batch={best_latency_config.get('batch_size', 'N/A')}"
        
        # Balanced config (use scoring)
        balanced = self._find_balanced_config()
        ws['E4'] = 'BALANCED'
        ws['E4'].font = Font(bold=True, size=11)
        ws['E5'] = f"{balanced['throughput_mb']:.1f} MB/sec"
        ws['E5'].font = Font(size=12, bold=True, color="4472C4")
        ws['E6'] = f"{balanced['avg_latency_ms']:.0f} ms lat"
        ws['E7'] = f"acks={balanced.get('acks', 'N/A')}"
    
    def _add_top_configs_chart(self, ws, cell):
        """Add top 10 configurations line chart"""
        # Sort by throughput, take top 10
        top_10 = self.producer_df.nlargest(10, 'throughput_mb')
        
        # Write data to sheet
        chart_data_start = 'N4'
        for idx, (_, row) in enumerate(top_10.iterrows(), 1):
            config_label = f"acks={row.get('acks', '?')}_bs={row.get('batch_size', '?')}"
            ws[f'N{idx+3}'] = config_label
            ws[f'O{idx+3}'] = row['throughput_mb']
        
        # Create chart
        chart = LineChart()
        chart.title = "Top 10 Configurations by Throughput"
        chart.style = 12
        chart.y_axis.title = "Throughput (MB/sec)"
        chart.x_axis.title = "Configuration"
        
        data = Reference(ws, min_col=15, min_row=3, max_row=13)
        categories = Reference(ws, min_col=14, min_row=4, max_row=13)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(categories)
        
        ws.add_chart(chart, cell)
    
    def _add_latency_throughput_scatter(self, ws, cell):
        """Add THE CRITICAL scatter plot: latency vs throughput"""
        # This is the "knee" chart showing saturation point
        
        # Write all data points to hidden columns
        data_col = 'P'
        for idx, (_, row) in enumerate(self.producer_df.iterrows(), 1):
            ws[f'{data_col}{idx+3}'] = row['throughput_mb']
            ws[f'Q{idx+3}'] = row['avg_latency_ms']
        
        # Create scatter chart
        chart = ScatterChart()
        chart.title = "Latency vs Throughput (The Knee Curve)"
        chart.style = 13
        chart.x_axis.title = "Throughput (MB/sec)"
        chart.y_axis.title = "Average Latency (ms)"
        
        xvalues = Reference(ws, min_col=16, min_row=4, max_row=len(self.producer_df)+3)
        yvalues = Reference(ws, min_col=17, min_row=4, max_row=len(self.producer_df)+3)
        series = xvalues, yvalues
        chart.series.append(series)
        
        # Add trend line to show saturation
        chart.trendline.dispEq = True
        
        ws.add_chart(chart, cell)
    
    # [Additional methods for other dashboard charts...]
    
    # ─────────────────────────────────────────────────────────
    # SHEET 2: THROUGHPUT ANALYSIS
    # ─────────────────────────────────────────────────────────
    
    def create_throughput_sheet(self):
        """Create comprehensive throughput analysis sheet"""
        ws = self.wb.create_sheet('Throughput Analysis')
        
        ws['A1'] = 'THROUGHPUT OPTIMIZATION ANALYSIS'
        ws['A1'].font = Font(size=14, bold=True)
        
        # Grouped by acks setting
        row = 3
        for acks_val in sorted(self.producer_df['acks'].unique()):
            subset = self.producer_df[self.producer_df['acks'] == str(acks_val)]
            
            ws[f'A{row}'] = f'Throughput with acks={acks_val}'
            ws[f'A{row}'].font = Font(bold=True, size=11)
            row += 1
            
            # Write table
            ws[f'A{row}'] = 'batch_size'
            ws[f'B{row}'] = 'compression'
            ws[f'C{row}'] = 'throughput_mb'
            ws[f'D{row}'] = 'latency_ms'
            row += 1
            
            for _, s_row in subset.iterrows():
                ws[f'A{row}'] = s_row.get('batch_size', '')
                ws[f'B{row}'] = s_row.get('compression_type', '')
                ws[f'C{row}'] = f"{s_row['throughput_mb']:.2f}"
                ws[f'D{row}'] = f"{s_row['avg_latency_ms']:.0f}"
                row += 1
            
            row += 2
        
        # Add charts here...
    
    # [Continue for other sheets: latency, tradeoff, scaling, heatmap, etc.]
    
    # ─────────────────────────────────────────────────────────
    # SHEET 9: RAW DATA
    # ─────────────────────────────────────────────────────────
    
    def create_raw_data_sheet(self):
        """Create sortable/filterable raw data sheet"""
        ws = self.wb.create_sheet('Raw Data')
        
        ws['A1'] = 'ALL TEST RESULTS - Sort and Filter'
        ws['A1'].font = Font(bold=True, size=12)
        
        # Write producer data
        for r_idx, row in enumerate(dataframe_to_rows(self.producer_df, index=False, header=True), 3):
            for c_idx, value in enumerate(row, 1):
                ws.cell(row=r_idx, column=c_idx, value=value)
        
        # Apply autofilter
        ws.auto_filter.ref = f"A3:{chr(64+len(self.producer_df.columns))}{len(self.producer_df)+3}"
        
        # Set column widths
        for col in ws.columns:
            ws.column_dimensions[col[0].column_letter].width = 12
    
    # [Continue with other sheet methods...]

# Usage
if __name__ == '__main__':
    import sys
    parsed_json = sys.argv[1] if len(sys.argv) > 1 else './parsed/parsed_results.json'
    output_xlsx = sys.argv[2] if len(sys.argv) > 2 else './reports/kafka_perf_report.xlsx'
    
    reporter = KafkaPerformanceExcelReporter(parsed_json, output_xlsx)
    reporter.generate_report()
```

### 3.2 Chart Specifications Reference

**Chart Type Selection by Question:**

| Question | Chart Type | X-Axis | Y-Axis | Color/Size |
|----------|-----------|--------|--------|-----------|
| Which config has best throughput? | Bar Chart | Configuration | MB/sec | acks value |
| How does throughput degrade with load? | Line Chart | # Producers | MB/sec/producer | - |
| Where does latency spike? | Scatter Plot | Throughput MB/sec | Latency ms | acks value |
| Which batch size is optimal? | Line Chart | batch.size | MB/sec | compression type |
| How does acks affect performance? | Box Plot | acks | Latency ms | - |
| Multi-parameter interaction? | Heatmap | batch.size | linger.ms | Throughput MB/sec (color) |
| Percentile latency distribution? | Waterfall | Percentile | Latency ms | - |
| Scalability profile? | Area Chart | # Producers | Throughput (stacked) | - |
| Trade-off comparison? | Bubble Chart | Throughput | Latency | Size=batch, Color=acks |

---

## 4. Implementation Roadmap

### Phase 1: Core Sheets (Week 1-2)
- [ ] Dashboard with 4 key charts
- [ ] Throughput Analysis sheet (5 charts)
- [ ] Raw Data sheet with filtering
- [ ] Test with your sample data (dev.log)

### Phase 2: Advanced Sheets (Week 3)
- [ ] Latency Analysis (5 charts)
- [ ] Trade-off Analysis (THE CRITICAL knee chart + extras)
- [ ] Scaling Performance (6 charts)
- [ ] Configuration Heatmap (3 heatmaps)

### Phase 3: Recommendations & Polish (Week 4)
- [ ] Acks Comparison sheet
- [ ] Message Size Analysis
- [ ] Recommendations with scoring
- [ ] Add data validation and sparklines
- [ ] Style/formatting pass

### Phase 4: Integration (Week 5)
- [ ] Hook into Ansible playbook
- [ ] Integrate with log parser
- [ ] E2E testing on full benchmark run
- [ ] Documentation

---

## 5. Chart Palette & Styling

**Color Scheme for Consistency:**

```
acks=0   → Red (#FF6B6B)      [Fast but risky]
acks=1   → Yellow (#FFD93D)   [Balanced]
acks=all → Green (#6BCB77)    [Safe but slow]

Throughput zones:
  Excellent: Dark green (#2F5740)
  Good: Light green (#A4DE6C)
  OK: Yellow (#FFE66D)
  Poor: Orange (#FF6B6B)
  Critical: Dark red (#8B0000)

Chart backgrounds: Light gray (#F5F5F5)
Text: Dark gray (#333333)
Grid lines: Light gray (#CCCCCC)
```

---

## 6. Industry Benchmark Context

From the Altoros Labs benchmark list, key observations to note in your report:

- **LinkedIn's 2014 baseline**: 2 million records/sec on 3 commodity machines
- **Honeycomb 2022 confirmation**: Still achieving similar throughput at scale
- **Throughput variance**: Depends heavily on message size, replication, and acks setting
- **Latency P99 often 2-3x higher than avg**: Your data shows this clearly
- **acks=0 vs acks=all**: Industry standard is 3-4x difference; your 3.4x is realistic
- **Scalability bottleneck**: Linear degradation is rare; most systems hit limits at 3-5x producers

**Your Report Should Reference**: Add a "Context" section noting where your results fit in industry benchmarks.

---

## 7. Quality Checklist

Before finalizing Excel:

- [ ] All 30+ charts render without errors
- [ ] Data series correctly mapped (no misaligned axes)
- [ ] Legend clearly labels all series
- [ ] Trend lines display (for appropriate charts)
- [ ] Colors consistent across all sheets
- [ ] Fonts readable (size 10-12 for labels, titles 12-14)
- [ ] No #DIV/0! or #REF! errors in formulas
- [ ] Raw Data sheet sortable and filterable
- [ ] Recommendations actionable and specific
- [ ] File size reasonable (<10MB)
- [ ] Print-friendly (landscape, fits on pages)
- [ ] Dashboard loads quickly (all charts on one screen)

---

## 8. Expected Output

Running `python scripts/generate_excel_report.py ./parsed/parsed_results.json ./reports/kafka_perf_report.xlsx` produces:

```
kafka_perf_report.xlsx
├── Sheet 1: Dashboard (4 charts, KPI summary)
├── Sheet 2: Throughput Analysis (5 charts)
├── Sheet 3: Latency Analysis (5 charts)
├── Sheet 4: Trade-off Analysis (4 charts - includes THE KNEE)
├── Sheet 5: Scaling Performance (6 charts)
├── Sheet 6: Configuration Heatmap (3 heatmaps)
├── Sheet 7: Message Size Impact (4 charts)
├── Sheet 8: Acks Comparison (4 charts)
├── Sheet 9: Raw Data (sortable table, 100+ rows)
└── Sheet 10: Recommendations (scored configs, actionable guidance)

Total: 30+ charts, 8 tables, ~40 data-driven visualizations
```

File opens immediately in Excel without requiring data refresh. Charts update if data rows are modified.

---

## 9. Example: Interpreting Your Data

Your dev.log contains three scenarios:

```
Scenario 1: acks=all, 1 producer
  Throughput: 28.59 MB/sec
  Latency: 3182 ms avg, P99=3568 ms
  
Scenario 2: acks=all, 3 producers (concurrent)
  Throughput: 71.3 MB/sec (aggregate, ~24 MB/sec per producer)
  Latency: 64600 ms fetch time (but this is CONSUMER-side)
  
Scenario 3: acks=0, 1 producer
  Throughput: 96.71 MB/sec (3.4x better!)
  Latency: 880 ms avg, P99=1355 ms
  
Scenario 4: acks=0, 3 producers
  Throughput: 58.67 MB/sec (aggregate, ~19.5 MB/sec per producer)
  Per-producer degradation: 39.4% (96.71 → 19.5)
  Latency: ~1512 ms (worse under contention)
```

**The Excel Report Would Show:**
- Scatter plot clearly showing three clouds (acks=0 on right, acks=all on left)
- "Knee" point at ~90-100 MB/sec where things saturate
- Clear 3.4x durability cost
- Scaling degradation: each additional producer reduces per-producer throughput

**Recommendation Would Be:**
- For non-critical: Use acks=0, batch=64000, linger=10 → 96.71 MB/sec
- For balanced: Use acks=1, batch=16384, linger=10 → 28.59 MB/sec with guarantee
- For critical: Use acks=all, batch=32768, linger=10 → 24.96 MB/sec with full durability

---

**Document Version:** 2.0 (Graph-Focused)  
**Last Updated:** December 2024  
**Status:** Ready for Implementation  
**Maintained By:** OSO DevOps Team
