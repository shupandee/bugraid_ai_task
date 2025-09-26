# Synthetic MELT Data Generator

A comprehensive synthetic data generator for MELT (Metrics, Events, Logs, Traces) data designed for testing anomaly detection and Root Cause Analysis (RCA) systems.

## Overview

This tool generates realistic synthetic observability data that includes:
- **Metrics**: Time-series data with configurable spikes and anomalies
- **Events**: Random operational events and incident-related events
- **Logs**: Structured logs with error bursts and debug noise
- **Traces**: Distributed tracing data with spans and missing links

## Features

- 🎯 **Realistic Data**: Generates data patterns that mirror real-world scenarios
- 📈 **Scalable Volume**: Support for data generation from 100MB to 10GB+
- 🚨 **Anomaly Injection**: Built-in anomaly patterns (CPU spikes, service outages, etc.)
- 🔄 **Reproducible**: Uses random seeds for consistent data generation
- 🐳 **Dockerized**: Complete containerized solution
- 📊 **Schema Documentation**: Well-documented data schemas
- 🧪 **Test Ready**: Designed for anomaly detection pipeline testing

## Quick Start

### Using Docker (Recommended)

```bash
# Build the container
docker build -t synthetic-melt-generator .

# Generate sample data (1GB)
docker run -v $(pwd)/output:/app/output synthetic-melt-generator \
  --size 1GB --anomalies cpu_spike,service_outage --seed 42

# Generate large dataset (10GB) with multiple anomalies
docker run -v $(pwd)/output:/app/output synthetic-melt-generator \
  --size 10GB --anomalies all --seed 123
```

### Local Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Generate data
python -m synthetic_melt_generator.cli --size 500MB --anomalies cpu_spike --output ./data
```

## Architecture

### Core Components

1. **Data Generators**
   - `MetricsGenerator`: Time-series metrics with realistic patterns
   - `EventsGenerator`: Operational and incident events
   - `LogsGenerator`: Structured application logs
   - `TracesGenerator`: Distributed tracing spans

2. **Anomaly Injectors**
   - `CPUSpikeInjector`: CPU utilization anomalies
   - `ServiceOutageInjector`: Service availability issues
   - `LatencyInjector`: Response time spikes
   - `ErrorBurstInjector`: Error rate increases

3. **Volume Scaling**
   - Intelligent data multiplication
   - Memory-efficient streaming generation
   - Configurable time ranges and frequencies

## Data Schemas

### Metrics Schema
```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "metric_name": "cpu_usage",
  "value": 45.2,
  "labels": {
    "host": "web-01",
    "service": "api",
    "environment": "production"
  },
  "anomaly": false
}
```

### Events Schema
```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "event_type": "deployment",
  "severity": "info",
  "source": "ci-cd-pipeline",
  "message": "Service api-v2.1.0 deployed successfully",
  "metadata": {
    "version": "v2.1.0",
    "duration": "120s"
  }
}
```

### Logs Schema
```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "ERROR",
  "service": "payment-service",
  "message": "Database connection timeout",
  "trace_id": "abc123def456",
  "span_id": "789ghi012",
  "metadata": {
    "error_code": "DB_TIMEOUT",
    "retry_count": 3
  }
}
```

### Traces Schema
```json
{
  "trace_id": "abc123def456",
  "span_id": "789ghi012",
  "parent_span_id": "456def789",
  "operation_name": "database_query",
  "start_time": "2024-01-01T00:00:00Z",
  "duration": 150,
  "service": "user-service",
  "tags": {
    "db.type": "postgresql",
    "db.statement": "SELECT * FROM users"
  },
  "status": "ok"
}
```

## Configuration

### Environment Variables

```bash
# Data generation settings
MELT_OUTPUT_DIR=/app/output
MELT_DEFAULT_SIZE=1GB
MELT_DEFAULT_SEED=42

# Service simulation settings
MELT_SERVICES=api,web,database,cache,queue
MELT_HOSTS=web-01,web-02,db-01,cache-01
MELT_ENVIRONMENTS=production,staging,development
```

### Configuration File (config.yaml)

```yaml
generation:
  time_range:
    start: "2024-01-01T00:00:00Z"
    end: "2024-01-02T00:00:00Z"
  
  metrics:
    frequency: 30s
    services: ["api", "web", "database"]
    metric_types: ["cpu", "memory", "disk", "network"]
  
  logs:
    frequency: 1s
    error_rate: 0.05
    debug_ratio: 0.3
  
  traces:
    frequency: 10s
    missing_span_rate: 0.02
    max_depth: 5
  
  events:
    frequency: 300s
    incident_probability: 0.1

anomalies:
  cpu_spike:
    probability: 0.05
    duration: "5m"
    intensity: 3.0
  
  service_outage:
    probability: 0.01
    duration: "10m"
    affected_services: ["api", "database"]
```

## Usage Examples

### Basic Generation

```python
from synthetic_melt_generator import MeltGenerator

# Initialize generator
generator = MeltGenerator(seed=42)

# Generate 1GB of data
data = generator.generate(
    size="1GB",
    anomalies=["cpu_spike", "service_outage"],
    output_format="json"
)

# Save to files
generator.save(data, output_dir="./output")
```

### Custom Anomaly Injection

```python
from synthetic_melt_generator.anomalies import CPUSpikeInjector

# Create custom anomaly
cpu_injector = CPUSpikeInjector(
    probability=0.1,
    duration_minutes=5,
    spike_multiplier=4.0
)

# Apply to metrics
anomalous_metrics = cpu_injector.inject(normal_metrics)
```

### Streaming Generation (Large Datasets)

```python
from synthetic_melt_generator import StreamingGenerator

# For very large datasets (10GB+)
streaming_gen = StreamingGenerator(
    chunk_size="100MB",
    output_dir="./large_dataset"
)

# Generate in chunks to avoid memory issues
for chunk in streaming_gen.generate_chunks(total_size="10GB"):
    streaming_gen.save_chunk(chunk)
```

## Testing & Validation

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/test_generators.py -v
pytest tests/test_anomalies.py -v
pytest tests/test_scaling.py -v

# Test with different data sizes
pytest tests/test_integration.py --size 100MB
pytest tests/test_integration.py --size 1GB
```

### Validation Scripts

```bash
# Validate generated data schemas
python scripts/validate_schemas.py --data-dir ./output

# Check anomaly detection compatibility
python scripts/test_anomaly_detection.py --data-dir ./output

# Performance benchmarks
python scripts/benchmark.py --sizes 100MB,1GB,5GB
```

## Monitoring & Metrics

The generator includes built-in monitoring for:

- **Generation Rate**: Records/second generated
- **Memory Usage**: Peak memory consumption
- **Anomaly Distribution**: Percentage of anomalous data points
- **Schema Compliance**: Validation success rate
- **File Size Accuracy**: Generated vs. target size

### Prometheus Metrics

```
# HELP melt_generator_records_total Total records generated
# TYPE melt_generator_records_total counter
melt_generator_records_total{type="metrics"} 1000000

# HELP melt_generator_anomalies_total Total anomalies injected
# TYPE melt_generator_anomalies_total counter
melt_generator_anomalies_total{type="cpu_spike"} 50

# HELP melt_generator_generation_duration_seconds Time spent generating data
# TYPE melt_generator_generation_duration_seconds histogram
melt_generator_generation_duration_seconds_bucket{le="10"} 5
```

## Design Choices & Trade-offs

### Design Decisions

1. **Modular Architecture**: Separate generators for each data type allow independent scaling and customization
2. **Streaming Generation**: Enables large dataset creation without memory constraints
3. **Configurable Anomalies**: Pluggable anomaly injection system for flexible testing scenarios
4. **Schema Validation**: Built-in validation ensures data quality and compatibility

### Trade-offs

1. **Realism vs. Performance**: More realistic data patterns require more computation
2. **Memory vs. Disk**: Streaming reduces memory usage but increases I/O operations
3. **Flexibility vs. Simplicity**: Rich configuration options add complexity
4. **Determinism vs. Variety**: Random seeds ensure reproducibility but may limit data diversity

### Performance Characteristics

- **Generation Rate**: ~10,000 records/second (varies by data type)
- **Memory Usage**: <500MB for datasets up to 10GB (streaming mode)
- **Disk I/O**: Optimized batch writes, ~100MB/s write throughput
- **CPU Usage**: Multi-threaded generation, scales with available cores

## API Reference

### Core Classes

#### MeltGenerator
Main generator class for coordinating data generation.

```python
class MeltGenerator:
    def __init__(self, seed: int = None, config: dict = None)
    def generate(self, size: str, anomalies: List[str] = None) -> MeltData
    def save(self, data: MeltData, output_dir: str) -> None
```

#### Individual Generators
- `MetricsGenerator`: Time-series metrics generation
- `EventsGenerator`: Event data generation  
- `LogsGenerator`: Log message generation
- `TracesGenerator`: Distributed trace generation

### Anomaly Injectors
- `CPUSpikeInjector`: CPU utilization spikes
- `ServiceOutageInjector`: Service availability issues
- `LatencyInjector`: Response time anomalies
- `ErrorBurstInjector`: Error rate increases

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone repository
git clone https://github.com/your-org/synthetic-melt-generator.git
cd synthetic-melt-generator

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: support@your-org.com
- 💬 Slack: #synthetic-data-generator
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/synthetic-melt-generator/issues)
- 📖 Documentation: [Full Documentation](https://docs.your-org.com/synthetic-melt-generator)
