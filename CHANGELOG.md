# Changelog

All notable changes to the `osodevops.kafka_perf_testing` collection will be documented in this file.

## [1.0.0] - 2025-02-12

### Features

- 7 Ansible roles for end-to-end Kafka performance testing
  - `setup_environment` - Test environment provisioning and validation
  - `perf_producer` - Kafka producer performance benchmarking
  - `perf_consumer` - Kafka consumer performance benchmarking
  - `log_parser` - Structured JSON parsing of test logs
  - `excel_generator` - Automated Excel report generation with 30+ charts
  - `cleanup` - Post-test cleanup and archival
  - `tests` - Core test orchestration
- 17 playbooks covering 5 test scenarios
  - Producer baseline benchmarks
  - Consumer baseline benchmarks
  - Load scaling tests
  - Message size impact analysis
  - Acks trade-off analysis
- Python scripts for log parsing and Excel report generation
  - 10-sheet workbook with dashboard, throughput, latency, trade-off, and scaling analysis
  - Scored configuration recommendations by use case
- Parametrized test matrices with baseline and quick profiles
- SSL/SASL authentication support
- Docker Compose local development environment
- Offline/air-gapped installation support
