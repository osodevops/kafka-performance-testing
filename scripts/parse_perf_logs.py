#!/usr/bin/env python3
"""
Kafka Performance Log Parser

Parses kafka-producer-perf-test and kafka-consumer-perf-test output logs
and extracts metrics into structured JSON format.

Usage:
    python parse_perf_logs.py <log_directory> <output_directory>
    python parse_perf_logs.py ./results/raw_logs ./results/parsed_data

Example:
    python parse_perf_logs.py --log-dir ./logs --output-dir ./parsed --verbose
"""

import re
import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any


class KafkaPerformanceParser:
    """
    Parser for Kafka performance test output logs.

    Handles both producer and consumer performance test outputs,
    extracting configuration metadata and performance metrics.
    """

    # Producer output pattern - matches final summary line
    # Example: 1000000 records sent, 14637.645096 records/sec (28.59 MB/sec),
    #          3182.27 ms avg latency, 3613.00 ms max latency,
    #          3289 ms 50th, 3467 ms 95th, 3568 ms 99th, 3603 ms 99.9th.
    PRODUCER_FINAL_PATTERN = re.compile(
        r'(\d+)\s+records sent,\s+'
        r'([\d.]+)\s+records/sec\s+\(([\d.]+)\s+MB/sec\),\s+'
        r'([\d.]+)\s+ms avg latency,\s+'
        r'([\d.]+)\s+ms max latency'
        r'(?:,\s+(\d+)\s+ms 50th)?'
        r'(?:,\s+(\d+)\s+ms 95th)?'
        r'(?:,\s+(\d+)\s+ms 99th)?'
        r'(?:,\s+(\d+)\s+ms 99\.9th)?'
    )

    # Producer intermediate output pattern (progress lines)
    PRODUCER_PROGRESS_PATTERN = re.compile(
        r'(\d+)\s+records sent,\s+'
        r'([\d.]+)\s+records/sec\s+\(([\d.]+)\s+MB/sec\),\s+'
        r'([\d.]+)\s+ms avg latency,\s+'
        r'([\d.]+)\s+ms max latency\.'
    )

    # Consumer output pattern - CSV format
    # Example: 2024-08-28 12:00:45:269, 2024-08-28 12:01:53:199, 1953.1250, 28.7520,
    #          1000000, 14721.0364, 3330, 64600, 30.2341, 15479.8762
    CONSUMER_PATTERN = re.compile(
        r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}:\d{3}),\s*'
        r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}:\d{3}),\s*'
        r'([\d.]+),\s*([\d.]+),\s*(\d+),\s*([\d.]+),\s*'
        r'(\d+),\s*(\d+),\s*([\d.]+),\s*([\d.]+)'
    )

    # Configuration patterns from log header comments
    CONFIG_PATTERN = re.compile(r'#\s*Configuration:\s*(.+)')
    RECORD_SIZE_PATTERN = re.compile(r'#\s*Record Size:\s*(\d+)')
    NUM_RECORDS_PATTERN = re.compile(r'#\s*Num Records:\s*(\d+)')
    SCENARIO_PATTERN = re.compile(r'#\s*(?:Producer|Consumer) (?:Performance )?Test\s*-\s*(.+)')
    TEST_RUN_PATTERN = re.compile(r'#\s*Test Run:\s*(.+)')
    HOST_PATTERN = re.compile(r'#\s*Host:\s*(.+)')
    DATE_PATTERN = re.compile(r'#\s*Date:\s*(.+)')

    def __init__(self, log_dir: str, output_dir: str, verbose: bool = False):
        """
        Initialize the parser.

        Args:
            log_dir: Directory containing raw log files
            output_dir: Directory to write parsed JSON output
            verbose: Enable verbose logging
        """
        self.log_dir = Path(log_dir)
        self.output_dir = Path(output_dir)
        self.verbose = verbose

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def log(self, message: str) -> None:
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(f"[INFO] {message}")

    def parse_producer_log(self, filepath: Path) -> Optional[Dict[str, Any]]:
        """
        Parse a producer performance test log file.

        Args:
            filepath: Path to the producer log file

        Returns:
            Dictionary containing configuration and metrics, or None if parsing fails
        """
        self.log(f"Parsing producer log: {filepath.name}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"[ERROR] Failed to read {filepath}: {e}")
            return None

        # Extract configuration from header comments
        config = self._extract_config_from_content(content)
        config.update(self._extract_config_from_filename(filepath, 'producer'))

        # Find all producer output lines and get the final summary
        final_matches = list(self.PRODUCER_FINAL_PATTERN.finditer(content))

        if not final_matches:
            # Try progress pattern if final pattern doesn't match
            progress_matches = list(self.PRODUCER_PROGRESS_PATTERN.finditer(content))
            if progress_matches:
                match = progress_matches[-1]
                metrics = {
                    'records_sent': int(match.group(1)),
                    'throughput_rps': float(match.group(2)),
                    'throughput_mb': float(match.group(3)),
                    'avg_latency_ms': float(match.group(4)),
                    'max_latency_ms': float(match.group(5)),
                    'p50_ms': None,
                    'p95_ms': None,
                    'p99_ms': None,
                    'p999_ms': None,
                }
            else:
                print(f"[WARN] No producer metrics found in {filepath.name}")
                return None
        else:
            match = final_matches[-1]
            metrics = {
                'records_sent': int(match.group(1)),
                'throughput_rps': float(match.group(2)),
                'throughput_mb': float(match.group(3)),
                'avg_latency_ms': float(match.group(4)),
                'max_latency_ms': float(match.group(5)),
                'p50_ms': int(match.group(6)) if match.group(6) else None,
                'p95_ms': int(match.group(7)) if match.group(7) else None,
                'p99_ms': int(match.group(8)) if match.group(8) else None,
                'p999_ms': int(match.group(9)) if match.group(9) else None,
            }

        return {
            'test_type': 'producer',
            'scenario': config.get('scenario', 'unknown'),
            'configuration': config,
            'metrics': metrics,
            'filepath': str(filepath),
            'filename': filepath.name,
            'parse_time': datetime.now().isoformat()
        }

    def parse_consumer_log(self, filepath: Path) -> Optional[Dict[str, Any]]:
        """
        Parse a consumer performance test log file.

        Args:
            filepath: Path to the consumer log file

        Returns:
            Dictionary containing configuration and metrics, or None if parsing fails
        """
        self.log(f"Parsing consumer log: {filepath.name}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"[ERROR] Failed to read {filepath}: {e}")
            return None

        # Extract configuration from header comments
        config = self._extract_config_from_content(content)
        config.update(self._extract_config_from_filename(filepath, 'consumer'))

        # Find consumer metrics (skip CSV header line)
        metrics = {}
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('start.time') or line.startswith('#') or not line:
                continue

            match = self.CONSUMER_PATTERN.search(line)
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

        if not metrics:
            print(f"[WARN] No consumer metrics found in {filepath.name}")
            return None

        return {
            'test_type': 'consumer',
            'scenario': config.get('scenario', 'unknown'),
            'configuration': config,
            'metrics': metrics,
            'filepath': str(filepath),
            'filename': filepath.name,
            'parse_time': datetime.now().isoformat()
        }

    def _extract_config_from_content(self, content: str) -> Dict[str, Any]:
        """
        Extract configuration from log file header comments.

        Args:
            content: Full content of the log file

        Returns:
            Dictionary of configuration values
        """
        config = {}

        # Extract scenario name
        match = self.SCENARIO_PATTERN.search(content)
        if match:
            config['scenario'] = match.group(1).strip()

        # Extract test run timestamp
        match = self.TEST_RUN_PATTERN.search(content)
        if match:
            config['test_run'] = match.group(1).strip()

        # Extract host
        match = self.HOST_PATTERN.search(content)
        if match:
            config['host'] = match.group(1).strip()

        # Extract date
        match = self.DATE_PATTERN.search(content)
        if match:
            config['date'] = match.group(1).strip()

        # Extract record size
        match = self.RECORD_SIZE_PATTERN.search(content)
        if match:
            config['record_size'] = int(match.group(1))

        # Extract num records
        match = self.NUM_RECORDS_PATTERN.search(content)
        if match:
            config['num_records'] = int(match.group(1))

        # Extract configuration key-value pairs
        # Example: # Configuration: acks=1, batch.size=16384, linger.ms=10, compression.type=zstd
        match = self.CONFIG_PATTERN.search(content)
        if match:
            config_str = match.group(1)
            for item in config_str.split(','):
                item = item.strip()
                if '=' in item:
                    key, value = item.split('=', 1)
                    key = key.strip().replace('.', '_')  # Normalize key names
                    value = value.strip()
                    # Try to convert to appropriate type
                    try:
                        if value.isdigit():
                            value = int(value)
                        elif value.replace('.', '').isdigit():
                            value = float(value)
                    except (ValueError, AttributeError):
                        pass
                    config[key] = value

        return config

    def _extract_config_from_filename(self, filepath: Path, test_type: str) -> Dict[str, Any]:
        """
        Extract configuration from filename convention.

        Expected format: producer_baseline_acks_1_batch_16384_linger_10_zstd_size_1024_timestamp.log

        Args:
            filepath: Path to the log file
            test_type: Either 'producer' or 'consumer'

        Returns:
            Dictionary of configuration values from filename
        """
        config = {}
        filename = filepath.stem  # Get filename without extension

        # Remove timestamp suffix (typically last part after last underscore with digits)
        parts = filename.split('_')

        # Try to extract known configuration patterns
        patterns = {
            'acks': r'acks[_-]?(\w+)',
            'batch': r'batch[_-]?(\d+)',
            'linger': r'linger[_-]?(\d+)',
            'size': r'size[_-]?(\d+)',
            'compression': r'(none|snappy|lz4|zstd|gzip)',
            'fetch': r'fetch[_-]?(\d+)',
            'poll': r'poll[_-]?(\d+)',
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                value = match.group(1)
                try:
                    if value.isdigit():
                        value = int(value)
                except (ValueError, AttributeError):
                    pass
                config[key] = value

        # Extract scenario name (typically second part of filename)
        if len(parts) >= 2 and parts[0] == test_type:
            config['scenario'] = parts[1]

        return config

    def parse_all_logs(self) -> List[Dict[str, Any]]:
        """
        Parse all log files in the log directory.

        Returns:
            List of parsed result dictionaries
        """
        all_results = []

        # Find all .log files
        log_files = list(self.log_dir.glob('*.log'))

        if not log_files:
            print(f"[WARN] No log files found in {self.log_dir}")
            return all_results

        self.log(f"Found {len(log_files)} log files to parse")

        for log_file in sorted(log_files):
            try:
                filename_lower = log_file.name.lower()

                if 'producer' in filename_lower:
                    result = self.parse_producer_log(log_file)
                elif 'consumer' in filename_lower:
                    result = self.parse_consumer_log(log_file)
                else:
                    # Try to detect from content
                    with open(log_file, 'r', encoding='utf-8') as f:
                        content = f.read(1000)  # Read first 1000 chars

                    if 'Producer' in content or 'records sent' in content:
                        result = self.parse_producer_log(log_file)
                    elif 'Consumer' in content or 'start.time' in content:
                        result = self.parse_consumer_log(log_file)
                    else:
                        self.log(f"Skipping unknown log type: {log_file.name}")
                        continue

                if result:
                    all_results.append(result)
                    self.log(f"Successfully parsed: {log_file.name}")

            except Exception as e:
                print(f"[ERROR] Failed to parse {log_file.name}: {e}")

        return all_results

    def save_results(self, results: List[Dict[str, Any]],
                     output_filename: Optional[str] = None) -> str:
        """
        Save parsed results to JSON file.

        Args:
            results: List of parsed result dictionaries
            output_filename: Optional specific filename (otherwise auto-generated)

        Returns:
            Path to the saved JSON file
        """
        if output_filename:
            output_file = self.output_dir / output_filename
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"parsed_results_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)

        self.log(f"Results saved to: {output_file}")
        return str(output_file)

    def save_individual_results(self, results: List[Dict[str, Any]]) -> List[str]:
        """
        Save each result to individual JSON files.

        Args:
            results: List of parsed result dictionaries

        Returns:
            List of paths to saved files
        """
        saved_files = []

        for result in results:
            # Create filename from original log filename
            original_name = Path(result.get('filename', 'unknown')).stem
            output_file = self.output_dir / f"{original_name}.json"

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=str)

            saved_files.append(str(output_file))

        return saved_files


def main():
    """Main entry point for the parser script."""
    parser = argparse.ArgumentParser(
        description='Parse Kafka performance test logs into structured JSON',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ./logs ./parsed
  %(prog)s --log-dir ./results/raw_logs --output-dir ./results/parsed_data
  %(prog)s ./logs ./parsed --verbose --individual
        """
    )

    parser.add_argument(
        'log_dir',
        nargs='?',
        default='./results/raw_logs',
        help='Directory containing raw log files (default: ./results/raw_logs)'
    )

    parser.add_argument(
        'output_dir',
        nargs='?',
        default='./results/parsed_data',
        help='Directory to write parsed JSON output (default: ./results/parsed_data)'
    )

    parser.add_argument(
        '--log-dir', '-l',
        dest='log_dir_opt',
        help='Alternative way to specify log directory'
    )

    parser.add_argument(
        '--output-dir', '-o',
        dest='output_dir_opt',
        help='Alternative way to specify output directory'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--individual', '-i',
        action='store_true',
        help='Save each result to individual JSON files'
    )

    parser.add_argument(
        '--output-file', '-f',
        help='Specific output filename (instead of auto-generated)'
    )

    args = parser.parse_args()

    # Handle alternative argument forms
    log_dir = args.log_dir_opt or args.log_dir
    output_dir = args.output_dir_opt or args.output_dir

    # Validate input directory
    if not os.path.isdir(log_dir):
        print(f"[ERROR] Log directory does not exist: {log_dir}")
        sys.exit(1)

    # Create parser and run
    perf_parser = KafkaPerformanceParser(log_dir, output_dir, verbose=args.verbose)
    results = perf_parser.parse_all_logs()

    if not results:
        print("[WARN] No results parsed. Check log directory and file formats.")
        sys.exit(0)

    # Save results
    if args.individual:
        saved_files = perf_parser.save_individual_results(results)
        print(f"Saved {len(saved_files)} individual JSON files to {output_dir}")
    else:
        output_file = perf_parser.save_results(results, args.output_file)
        print(f"Parsed {len(results)} log files. Results saved to: {output_file}")

    # Print summary
    producer_count = sum(1 for r in results if r['test_type'] == 'producer')
    consumer_count = sum(1 for r in results if r['test_type'] == 'consumer')
    print(f"\nSummary:")
    print(f"  Producer tests: {producer_count}")
    print(f"  Consumer tests: {consumer_count}")
    print(f"  Total: {len(results)}")


if __name__ == '__main__':
    main()
