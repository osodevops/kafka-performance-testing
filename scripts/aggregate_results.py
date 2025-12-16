#!/usr/bin/env python3
"""
Kafka Performance Results Aggregator

Aggregates multiple test run results for statistical analysis and comparison.
Combines parsed JSON files and calculates statistics across test runs.

Usage:
    python aggregate_results.py <input_dir> <output_file>
    python aggregate_results.py ./results/parsed_data ./results/aggregated_results.json

Features:
    - Combine multiple test run JSON files
    - Calculate mean, std, min, max, percentiles
    - Group by configuration for comparison
    - Export aggregated statistics to JSON or CSV
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict

try:
    import numpy as np
except ImportError:
    print("[ERROR] numpy is required. Install with: pip install numpy")
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    print("[ERROR] pandas is required. Install with: pip install pandas")
    sys.exit(1)


class ResultsAggregator:
    """
    Aggregator for Kafka performance test results.

    Combines multiple test runs, calculates statistics,
    and generates summary reports.
    """

    def __init__(self, input_dir: str, verbose: bool = False):
        """
        Initialize the aggregator.

        Args:
            input_dir: Directory containing parsed JSON files
            verbose: Enable verbose output
        """
        self.input_dir = Path(input_dir)
        self.verbose = verbose
        self.all_results: List[Dict[str, Any]] = []

    def log(self, message: str) -> None:
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(f"[INFO] {message}")

    def load_all_results(self) -> int:
        """
        Load all JSON result files from the input directory.

        Returns:
            Number of results loaded
        """
        json_files = list(self.input_dir.glob('*.json'))

        if not json_files:
            print(f"[WARN] No JSON files found in {self.input_dir}")
            return 0

        self.log(f"Found {len(json_files)} JSON files")

        for json_file in sorted(json_files):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Handle both single result and list of results
                if isinstance(data, list):
                    self.all_results.extend(data)
                    self.log(f"Loaded {len(data)} results from {json_file.name}")
                else:
                    self.all_results.append(data)
                    self.log(f"Loaded 1 result from {json_file.name}")

            except Exception as e:
                print(f"[ERROR] Failed to load {json_file}: {e}")

        return len(self.all_results)

    def _config_to_key(self, config: Dict[str, Any]) -> str:
        """
        Convert configuration dict to a hashable string key.

        Args:
            config: Configuration dictionary

        Returns:
            String key for grouping
        """
        # Select relevant keys for grouping
        relevant_keys = [
            'acks', 'batch_size', 'linger_ms', 'compression_type',
            'compression', 'record_size', 'fetch_min_bytes',
            'max_poll_records', 'num_producers', 'num_consumers'
        ]

        parts = []
        for key in sorted(relevant_keys):
            if key in config:
                parts.append(f"{key}={config[key]}")

        return "|".join(parts) if parts else "default"

    def aggregate_producer_results(self) -> Dict[str, Dict[str, Any]]:
        """
        Aggregate producer results by configuration.

        Returns:
            Dictionary mapping config keys to aggregated statistics
        """
        producer_results = [
            r for r in self.all_results
            if r.get('test_type') == 'producer'
        ]

        if not producer_results:
            return {}

        # Group by configuration
        groups = defaultdict(list)
        for result in producer_results:
            config = result.get('configuration', {})
            key = self._config_to_key(config)
            groups[key].append(result)

        # Calculate statistics for each group
        aggregated = {}
        for key, results in groups.items():
            metrics_list = [r.get('metrics', {}) for r in results]

            throughput_mb = [m.get('throughput_mb', 0) for m in metrics_list if m.get('throughput_mb')]
            throughput_rps = [m.get('throughput_rps', 0) for m in metrics_list if m.get('throughput_rps')]
            avg_latency = [m.get('avg_latency_ms', 0) for m in metrics_list if m.get('avg_latency_ms')]
            p99_latency = [m.get('p99_ms', 0) for m in metrics_list if m.get('p99_ms')]

            aggregated[key] = {
                'configuration': results[0].get('configuration', {}),
                'test_count': len(results),
                'throughput_mb': self._calc_stats(throughput_mb),
                'throughput_rps': self._calc_stats(throughput_rps),
                'avg_latency_ms': self._calc_stats(avg_latency),
                'p99_latency_ms': self._calc_stats(p99_latency),
            }

        return aggregated

    def aggregate_consumer_results(self) -> Dict[str, Dict[str, Any]]:
        """
        Aggregate consumer results by configuration.

        Returns:
            Dictionary mapping config keys to aggregated statistics
        """
        consumer_results = [
            r for r in self.all_results
            if r.get('test_type') == 'consumer'
        ]

        if not consumer_results:
            return {}

        # Group by configuration
        groups = defaultdict(list)
        for result in consumer_results:
            config = result.get('configuration', {})
            key = self._config_to_key(config)
            groups[key].append(result)

        # Calculate statistics for each group
        aggregated = {}
        for key, results in groups.items():
            metrics_list = [r.get('metrics', {}) for r in results]

            throughput_mb = [m.get('throughput_mb_sec', 0) for m in metrics_list if m.get('throughput_mb_sec')]
            throughput_msg = [m.get('throughput_msg_sec', 0) for m in metrics_list if m.get('throughput_msg_sec')]
            rebalance_time = [m.get('rebalance_time_ms', 0) for m in metrics_list if m.get('rebalance_time_ms') is not None]

            aggregated[key] = {
                'configuration': results[0].get('configuration', {}),
                'test_count': len(results),
                'throughput_mb_sec': self._calc_stats(throughput_mb),
                'throughput_msg_sec': self._calc_stats(throughput_msg),
                'rebalance_time_ms': self._calc_stats(rebalance_time),
            }

        return aggregated

    def _calc_stats(self, values: List[float]) -> Dict[str, float]:
        """
        Calculate statistics for a list of values.

        Args:
            values: List of numeric values

        Returns:
            Dictionary with statistical measures
        """
        if not values:
            return {
                'mean': None,
                'std': None,
                'min': None,
                'max': None,
                'p50': None,
                'p95': None,
                'p99': None,
                'count': 0
            }

        arr = np.array(values)
        return {
            'mean': float(np.mean(arr)),
            'std': float(np.std(arr)),
            'min': float(np.min(arr)),
            'max': float(np.max(arr)),
            'p50': float(np.percentile(arr, 50)),
            'p95': float(np.percentile(arr, 95)),
            'p99': float(np.percentile(arr, 99)),
            'count': len(values)
        }

    def generate_summary(self) -> Dict[str, Any]:
        """
        Generate a complete summary of all aggregated results.

        Returns:
            Dictionary containing full aggregation summary
        """
        producer_agg = self.aggregate_producer_results()
        consumer_agg = self.aggregate_consumer_results()

        # Find best configurations
        best_producer_throughput = None
        best_producer_latency = None

        if producer_agg:
            # Best throughput
            best_key = max(
                producer_agg.keys(),
                key=lambda k: producer_agg[k]['throughput_mb'].get('mean', 0) or 0
            )
            best_producer_throughput = {
                'config_key': best_key,
                **producer_agg[best_key]
            }

            # Best latency
            valid_latency = {
                k: v for k, v in producer_agg.items()
                if v['avg_latency_ms'].get('mean') is not None
            }
            if valid_latency:
                best_key = min(
                    valid_latency.keys(),
                    key=lambda k: valid_latency[k]['avg_latency_ms'].get('mean', float('inf'))
                )
                best_producer_latency = {
                    'config_key': best_key,
                    **producer_agg[best_key]
                }

        best_consumer_throughput = None
        if consumer_agg:
            best_key = max(
                consumer_agg.keys(),
                key=lambda k: consumer_agg[k]['throughput_mb_sec'].get('mean', 0) or 0
            )
            best_consumer_throughput = {
                'config_key': best_key,
                **consumer_agg[best_key]
            }

        return {
            'summary': {
                'total_results': len(self.all_results),
                'producer_results': len([r for r in self.all_results if r.get('test_type') == 'producer']),
                'consumer_results': len([r for r in self.all_results if r.get('test_type') == 'consumer']),
                'unique_producer_configs': len(producer_agg),
                'unique_consumer_configs': len(consumer_agg),
                'aggregation_time': datetime.now().isoformat(),
            },
            'best_configurations': {
                'producer_highest_throughput': best_producer_throughput,
                'producer_lowest_latency': best_producer_latency,
                'consumer_highest_throughput': best_consumer_throughput,
            },
            'producer_aggregations': producer_agg,
            'consumer_aggregations': consumer_agg,
        }

    def export_to_json(self, output_file: str) -> str:
        """
        Export aggregated results to JSON file.

        Args:
            output_file: Path to output file

        Returns:
            Path to created file
        """
        summary = self.generate_summary()

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, default=str)

        self.log(f"Exported aggregated results to: {output_path}")
        return str(output_path)

    def export_to_csv(self, output_file: str) -> str:
        """
        Export aggregated results to CSV file.

        Args:
            output_file: Path to output file

        Returns:
            Path to created file
        """
        summary = self.generate_summary()

        # Flatten producer aggregations
        rows = []

        for key, data in summary.get('producer_aggregations', {}).items():
            config = data.get('configuration', {})
            throughput = data.get('throughput_mb', {})
            latency = data.get('avg_latency_ms', {})

            rows.append({
                'test_type': 'producer',
                'config_key': key,
                'acks': config.get('acks', ''),
                'batch_size': config.get('batch_size', ''),
                'linger_ms': config.get('linger_ms', ''),
                'compression': config.get('compression_type', config.get('compression', '')),
                'record_size': config.get('record_size', ''),
                'test_count': data.get('test_count', 0),
                'throughput_mb_mean': throughput.get('mean', ''),
                'throughput_mb_std': throughput.get('std', ''),
                'latency_ms_mean': latency.get('mean', ''),
                'latency_ms_std': latency.get('std', ''),
            })

        for key, data in summary.get('consumer_aggregations', {}).items():
            config = data.get('configuration', {})
            throughput = data.get('throughput_mb_sec', {})

            rows.append({
                'test_type': 'consumer',
                'config_key': key,
                'fetch_min_bytes': config.get('fetch_min_bytes', ''),
                'max_poll_records': config.get('max_poll_records', ''),
                'test_count': data.get('test_count', 0),
                'throughput_mb_mean': throughput.get('mean', ''),
                'throughput_mb_std': throughput.get('std', ''),
            })

        df = pd.DataFrame(rows)

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        df.to_csv(output_path, index=False)

        self.log(f"Exported aggregated results to: {output_path}")
        return str(output_path)

    def print_summary(self) -> None:
        """Print a human-readable summary to stdout."""
        summary = self.generate_summary()

        print("\n" + "=" * 60)
        print("KAFKA PERFORMANCE TEST AGGREGATION SUMMARY")
        print("=" * 60)

        s = summary['summary']
        print(f"\nTotal Results: {s['total_results']}")
        print(f"  Producer tests: {s['producer_results']}")
        print(f"  Consumer tests: {s['consumer_results']}")
        print(f"  Unique producer configs: {s['unique_producer_configs']}")
        print(f"  Unique consumer configs: {s['unique_consumer_configs']}")

        best = summary['best_configurations']

        if best.get('producer_highest_throughput'):
            print("\n--- Best Producer (Throughput) ---")
            data = best['producer_highest_throughput']
            throughput = data.get('throughput_mb', {})
            print(f"  Config: {data.get('config_key')}")
            print(f"  Mean Throughput: {throughput.get('mean', 0):.2f} MB/sec")
            print(f"  Std Dev: {throughput.get('std', 0):.2f}")
            print(f"  Test Count: {data.get('test_count', 0)}")

        if best.get('producer_lowest_latency'):
            print("\n--- Best Producer (Latency) ---")
            data = best['producer_lowest_latency']
            latency = data.get('avg_latency_ms', {})
            print(f"  Config: {data.get('config_key')}")
            print(f"  Mean Latency: {latency.get('mean', 0):.2f} ms")
            print(f"  Std Dev: {latency.get('std', 0):.2f}")
            print(f"  Test Count: {data.get('test_count', 0)}")

        if best.get('consumer_highest_throughput'):
            print("\n--- Best Consumer (Throughput) ---")
            data = best['consumer_highest_throughput']
            throughput = data.get('throughput_mb_sec', {})
            print(f"  Config: {data.get('config_key')}")
            print(f"  Mean Throughput: {throughput.get('mean', 0):.2f} MB/sec")
            print(f"  Std Dev: {throughput.get('std', 0):.2f}")
            print(f"  Test Count: {data.get('test_count', 0)}")

        print("\n" + "=" * 60)


def main():
    """Main entry point for the aggregator script."""
    parser = argparse.ArgumentParser(
        description='Aggregate Kafka performance test results',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ./results/parsed_data aggregated.json
  %(prog)s ./parsed ./results/aggregated_results.json --verbose
  %(prog)s ./parsed ./results/summary.csv --format csv
        """
    )

    parser.add_argument(
        'input_dir',
        nargs='?',
        default='./results/parsed_data',
        help='Directory containing parsed JSON files (default: ./results/parsed_data)'
    )

    parser.add_argument(
        'output_file',
        nargs='?',
        default='./results/aggregated_results.json',
        help='Output file path (default: ./results/aggregated_results.json)'
    )

    parser.add_argument(
        '--format', '-f',
        choices=['json', 'csv'],
        default='json',
        help='Output format (default: json)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--print-summary', '-p',
        action='store_true',
        help='Print summary to stdout'
    )

    args = parser.parse_args()

    # Validate input directory
    if not Path(args.input_dir).is_dir():
        print(f"[ERROR] Input directory does not exist: {args.input_dir}")
        sys.exit(1)

    # Create aggregator and load results
    aggregator = ResultsAggregator(args.input_dir, verbose=args.verbose)
    count = aggregator.load_all_results()

    if count == 0:
        print("[WARN] No results loaded. Nothing to aggregate.")
        sys.exit(0)

    print(f"Loaded {count} test results")

    # Export results
    if args.format == 'csv':
        output_file = aggregator.export_to_csv(args.output_file)
    else:
        output_file = aggregator.export_to_json(args.output_file)

    print(f"Aggregated results saved to: {output_file}")

    # Print summary if requested
    if args.print_summary:
        aggregator.print_summary()


if __name__ == '__main__':
    main()
