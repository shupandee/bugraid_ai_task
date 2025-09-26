"""
Command-line interface for the synthetic MELT data generator.
"""

import click
import yaml
from datetime import datetime
from pathlib import Path
from typing import Optional

from .core.generator import MeltGenerator
from .core.streaming import StreamingGenerator
from .core.models import GenerationConfig, AnomalyConfig


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Synthetic MELT Data Generator - Generate realistic observability data for testing."""
    pass


@cli.command()
@click.option("--size", default="1GB", help="Target data size (e.g., 100MB, 1GB, 10GB)")
@click.option("--anomalies", help="Comma-separated list of anomalies to inject (cpu_spike,service_outage,latency_spike,error_burst,all)")
@click.option("--output", "-o", default="./output", help="Output directory")
@click.option("--seed", type=int, default=42, help="Random seed for reproducibility")
@click.option("--config", help="Path to YAML configuration file")
@click.option("--duration", type=int, default=24, help="Duration in hours")
@click.option("--services", help="Comma-separated list of services")
@click.option("--streaming", is_flag=True, help="Use streaming generation for large datasets")
def generate(size: str, anomalies: Optional[str], output: str, seed: int, config: Optional[str], 
             duration: int, services: Optional[str], streaming: bool):
    """Generate synthetic MELT data."""
    
    # Load configuration
    if config:
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)
        generation_config = GenerationConfig(**config_data.get('generation', {}))
        anomaly_config = AnomalyConfig(**config_data.get('anomalies', {}))
    else:
        generation_config = GenerationConfig(seed=seed, duration_hours=duration)
        anomaly_config = AnomalyConfig()
    
    # Override with CLI parameters
    if services:
        generation_config.services = [s.strip() for s in services.split(',')]
    
    # Parse anomalies
    anomaly_list = None
    if anomalies:
        anomaly_list = [a.strip() for a in anomalies.split(',')]
    
    # Choose generator based on streaming flag
    if streaming:
        click.echo("🌊 Using streaming generator for large dataset...")
        generator = StreamingGenerator(generation_config, anomaly_config)
        generator.generate_streaming(size, anomaly_list, output)
    else:
        click.echo("🚀 Starting standard generation...")
        generator = MeltGenerator(generation_config, anomaly_config)
        data = generator.generate(size, anomaly_list)
        generator.save(data, output)
    
    click.echo(f"✅ Generation complete! Data saved to {output}")


@cli.command()
@click.option("--data-dir", required=True, help="Directory containing generated data")
@click.option("--output", "-o", default="./validation_report.json", help="Output file for validation report")
def validate(data_dir: str, output: str):
    """Validate generated MELT data schemas and quality."""
    from .validation.validator import DataValidator
    
    click.echo(f"🔍 Validating data in {data_dir}...")
    
    validator = DataValidator()
    report = validator.validate_directory(data_dir)
    
    # Save validation report
    import json
    with open(output, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    # Print summary
    click.echo(f"\n📊 Validation Summary:")
    click.echo(f"   Total files: {report['summary']['total_files']}")
    click.echo(f"   Valid files: {report['summary']['valid_files']}")
    click.echo(f"   Invalid files: {report['summary']['invalid_files']}")
    click.echo(f"   Total records: {report['summary']['total_records']:,}")
    
    if report['summary']['invalid_files'] > 0:
        click.echo(f"❌ Validation failed! See {output} for details.")
        exit(1)
    else:
        click.echo(f"✅ All data is valid!")


@cli.command()
@click.option("--sizes", default="100MB,1GB,5GB", help="Comma-separated list of sizes to benchmark")
@click.option("--output", "-o", default="./benchmark_results.json", help="Output file for benchmark results")
@click.option("--iterations", type=int, default=3, help="Number of iterations per size")
def benchmark(sizes: str, output: str, iterations: int):
    """Benchmark generation performance across different data sizes."""
    from .benchmarks.performance import PerformanceBenchmark
    
    size_list = [s.strip() for s in sizes.split(',')]
    
    click.echo(f"🏃 Running performance benchmarks...")
    click.echo(f"   Sizes: {size_list}")
    click.echo(f"   Iterations: {iterations}")
    
    benchmark_runner = PerformanceBenchmark()
    results = benchmark_runner.run_benchmarks(size_list, iterations)
    
    # Save results
    import json
    with open(output, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Print summary
    click.echo(f"\n📊 Benchmark Results:")
    for size, result in results.items():
        click.echo(f"   {size}:")
        click.echo(f"     Avg time: {result['avg_time']:.2f}s")
        click.echo(f"     Avg rate: {result['avg_rate']:.0f} records/sec")
        click.echo(f"     Avg memory: {result['avg_memory']:.1f}MB")
    
    click.echo(f"📄 Detailed results saved to {output}")


@cli.command()
@click.option("--input-dir", required=True, help="Directory containing MELT data")
@click.option("--output", "-o", default="./anomaly_report.json", help="Output file for anomaly detection report")
def detect_anomalies(input_dir: str, output: str):
    """Test anomaly detection on generated data."""
    from .validation.anomaly_detector import AnomalyDetector
    
    click.echo(f"🔍 Detecting anomalies in {input_dir}...")
    
    detector = AnomalyDetector()
    report = detector.detect_anomalies(input_dir)
    
    # Save report
    import json
    with open(output, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    # Print summary
    click.echo(f"\n🚨 Anomaly Detection Summary:")
    click.echo(f"   Total anomalies detected: {report['summary']['total_anomalies']}")
    click.echo(f"   CPU spikes: {report['summary']['cpu_spikes']}")
    click.echo(f"   Latency spikes: {report['summary']['latency_spikes']}")
    click.echo(f"   Error bursts: {report['summary']['error_bursts']}")
    click.echo(f"   Service outages: {report['summary']['service_outages']}")
    
    click.echo(f"📄 Detailed report saved to {output}")


@cli.command()
def config_template():
    """Generate a template configuration file."""
    template = {
        "generation": {
            "seed": 42,
            "duration_hours": 24,
            "services": ["api", "web", "database", "cache", "queue"],
            "hosts": ["web-01", "web-02", "db-01", "cache-01"],
            "environments": ["production", "staging", "development"],
            "metrics_frequency_seconds": 30,
            "logs_frequency_seconds": 1,
            "traces_frequency_seconds": 10,
            "events_frequency_seconds": 300,
            "error_rate": 0.05,
            "debug_log_ratio": 0.3,
            "missing_span_rate": 0.02,
            "max_trace_depth": 5,
            "incident_probability": 0.1
        },
        "anomalies": {
            "cpu_spike": {
                "probability": 0.05,
                "duration_minutes": 5,
                "intensity": 3.0
            },
            "service_outage": {
                "probability": 0.01,
                "duration_minutes": 10,
                "affected_services": ["api", "database"]
            },
            "latency_spike": {
                "probability": 0.03,
                "duration_minutes": 3,
                "multiplier": 5.0
            },
            "error_burst": {
                "probability": 0.02,
                "duration_minutes": 2,
                "error_rate": 0.5
            }
        }
    }
    
    config_path = "melt_generator_config.yaml"
    with open(config_path, 'w') as f:
        yaml.dump(template, f, default_flow_style=False, indent=2)
    
    click.echo(f"📝 Configuration template saved to {config_path}")
    click.echo("Edit this file to customize your data generation settings.")


@cli.command()
@click.option("--data-dir", required=True, help="Directory containing MELT data")
def info(data_dir: str):
    """Display information about generated MELT data."""
    data_path = Path(data_dir)
    
    if not data_path.exists():
        click.echo(f"❌ Directory {data_dir} does not exist")
        exit(1)
    
    # Load metadata if available
    metadata_file = data_path / "metadata.json"
    stats_file = data_path / "statistics.json"
    
    if metadata_file.exists():
        import json
        with open(metadata_file) as f:
            metadata = json.load(f)
        
        click.echo(f"📊 MELT Data Information")
        click.echo(f"=" * 50)
        click.echo(f"Generated at: {metadata['generated_at']}")
        click.echo(f"Generator version: {metadata['generator_version']}")
        click.echo(f"Data types: {', '.join(metadata['data_types'])}")
        
        config = metadata['generation_config']
        click.echo(f"\n⚙️  Generation Configuration:")
        click.echo(f"   Duration: {config['duration_hours']} hours")
        click.echo(f"   Services: {', '.join(config['services'])}")
        click.echo(f"   Environments: {', '.join(config['environments'])}")
        click.echo(f"   Seed: {config['seed']}")
    
    if stats_file.exists():
        import json
        with open(stats_file) as f:
            stats = json.load(f)
        
        click.echo(f"\n📈 Generation Statistics:")
        click.echo(f"   Total records: {stats['total_records']:,}")
        click.echo(f"   Metrics: {stats['metrics_count']:,}")
        click.echo(f"   Events: {stats['events_count']:,}")
        click.echo(f"   Logs: {stats['logs_count']:,}")
        click.echo(f"   Traces: {stats['traces_count']:,}")
        click.echo(f"   Generation time: {stats['generation_time_seconds']:.2f}s")
        click.echo(f"   Generation rate: {stats['total_records'] / stats['generation_time_seconds']:.0f} records/sec")
        click.echo(f"   Output size: {stats['output_size_mb']:.1f}MB")
    
    # List data files
    click.echo(f"\n📁 Data Files:")
    for file_path in data_path.glob("*.jsonl"):
        file_size = file_path.stat().st_size / 1024 / 1024  # MB
        click.echo(f"   {file_path.name}: {file_size:.1f}MB")


if __name__ == "__main__":
    cli()
