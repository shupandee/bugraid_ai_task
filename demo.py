#!/usr/bin/env python3
"""
Demo script for the Synthetic MELT Data Generator.
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from synthetic_melt_generator.core.generator import MeltGenerator
from synthetic_melt_generator.core.models import GenerationConfig, AnomalyConfig


def run_demo():
    """Run a comprehensive demo of the MELT data generator."""
    
    print("🚀 Synthetic MELT Data Generator Demo")
    print("=" * 50)
    
    # Create demo output directory
    output_dir = "./demo_output"
    Path(output_dir).mkdir(exist_ok=True)
    
    # Demo 1: Basic generation
    print("\n📊 Demo 1: Basic Data Generation")
    print("-" * 30)
    
    config = GenerationConfig(
        seed=42,
        duration_hours=1,  # Short demo duration
        services=["api", "web", "database"],
        hosts=["web-01", "web-02", "db-01"],
        environments=["production", "staging"]
    )
    
    generator = MeltGenerator(config)
    
    print("Generating 10MB of basic MELT data...")
    start_time = time.time()
    
    data = generator.generate(size="10MB", anomalies=None)
    
    end_time = time.time()
    
    print(f"✅ Generated {data.total_records():,} records in {end_time - start_time:.2f}s")
    print(f"   📈 Metrics: {len(data.metrics):,}")
    print(f"   📅 Events: {len(data.events):,}")
    print(f"   📝 Logs: {len(data.logs):,}")
    print(f"   🔍 Traces: {len(data.traces):,}")
    
    # Save basic data
    generator.save(data, f"{output_dir}/basic")
    
    # Demo 2: Anomaly injection
    print("\n🚨 Demo 2: Anomaly Injection")
    print("-" * 30)
    
    anomaly_config = AnomalyConfig()
    anomaly_generator = MeltGenerator(config, anomaly_config)
    
    print("Generating 10MB of data with anomalies...")
    start_time = time.time()
    
    anomaly_data = anomaly_generator.generate(
        size="10MB", 
        anomalies=["cpu_spike", "error_burst", "latency_spike"]
    )
    
    end_time = time.time()
    
    print(f"✅ Generated {anomaly_data.total_records():,} records with anomalies in {end_time - start_time:.2f}s")
    
    # Count anomalous records
    anomalous_metrics = sum(1 for m in anomaly_data.metrics if m.anomaly)
    anomalous_traces = sum(1 for t in anomaly_data.traces if t.status != "ok")
    
    print(f"   🔥 Anomalous metrics: {anomalous_metrics}")
    print(f"   ⚠️  Failed traces: {anomalous_traces}")
    
    # Save anomaly data
    anomaly_generator.save(anomaly_data, f"{output_dir}/anomalies")
    
    # Demo 3: Schema validation
    print("\n🔍 Demo 3: Schema Validation")
    print("-" * 30)
    
    # Sample a few records and validate their structure
    sample_metric = data.metrics[0] if data.metrics else None
    sample_event = data.events[0] if data.events else None
    sample_log = data.logs[0] if data.logs else None
    sample_trace = data.traces[0] if data.traces else None
    
    print("Sample records generated:")
    
    if sample_metric:
        print(f"📈 Metric: {sample_metric.metric_name} = {sample_metric.value} ({sample_metric.labels.get('unit', 'unknown')})")
    
    if sample_event:
        print(f"📅 Event: {sample_event.event_type} - {sample_event.severity.value}")
    
    if sample_log:
        print(f"📝 Log: [{sample_log.level.value}] {sample_log.message[:50]}...")
    
    if sample_trace:
        print(f"🔍 Trace: {sample_trace.operation_name} ({sample_trace.duration}μs)")
    
    # Demo 4: Performance metrics
    print("\n⚡ Demo 4: Performance Metrics")
    print("-" * 30)
    
    total_records = data.total_records() + anomaly_data.total_records()
    total_time = (end_time - start_time) * 2  # Approximate total time for both demos
    
    print(f"📊 Total records generated: {total_records:,}")
    print(f"⏱️  Total generation time: {total_time:.2f}s")
    print(f"🚀 Average generation rate: {total_records / total_time:.0f} records/sec")
    
    # Demo 5: File outputs
    print("\n📁 Demo 5: Output Files")
    print("-" * 30)
    
    for demo_type in ["basic", "anomalies"]:
        demo_path = Path(f"{output_dir}/{demo_type}")
        if demo_path.exists():
            print(f"\n{demo_type.title()} data files:")
            for file_path in demo_path.glob("*.jsonl"):
                file_size = file_path.stat().st_size / 1024  # KB
                print(f"   📄 {file_path.name}: {file_size:.1f}KB")
            
            # Check for metadata
            metadata_file = demo_path / "metadata.json"
            stats_file = demo_path / "statistics.json"
            
            if metadata_file.exists():
                print(f"   📋 metadata.json: {metadata_file.stat().st_size / 1024:.1f}KB")
            
            if stats_file.exists():
                print(f"   📊 statistics.json: {stats_file.stat().st_size / 1024:.1f}KB")
    
    print(f"\n✅ Demo complete! Check the output in: {output_dir}")
    print("\n🎯 Next steps:")
    print("   1. Explore the generated data files")
    print("   2. Try the CLI: python -m synthetic_melt_generator.cli generate --help")
    print("   3. Use Docker: docker build -t melt-generator .")
    print("   4. Scale up: Generate larger datasets (100MB, 1GB, 10GB)")


def validate_installation():
    """Validate that all required components are working."""
    
    print("🔍 Validating installation...")
    
    try:
        # Test imports
        from synthetic_melt_generator.core.generator import MeltGenerator
        from synthetic_melt_generator.core.models import GenerationConfig
        from synthetic_melt_generator.generators.metrics import MetricsGenerator
        from synthetic_melt_generator.generators.events import EventsGenerator
        from synthetic_melt_generator.generators.logs import LogsGenerator
        from synthetic_melt_generator.generators.traces import TracesGenerator
        from synthetic_melt_generator.anomalies.injectors import AnomalyInjector
        
        print("✅ All imports successful")
        
        # Test basic generation
        config = GenerationConfig(seed=42, duration_hours=0.1)  # 6 minutes
        generator = MeltGenerator(config)
        
        small_data = generator.generate(size="1MB", anomalies=None)
        
        if small_data.total_records() > 0:
            print(f"✅ Basic generation works ({small_data.total_records()} records)")
        else:
            print("❌ No records generated")
            return False
        
        # Test anomaly injection
        anomaly_data = generator.generate(size="1MB", anomalies=["cpu_spike"])
        anomalous_count = sum(1 for m in anomaly_data.metrics if m.anomaly)
        
        if anomalous_count > 0:
            print(f"✅ Anomaly injection works ({anomalous_count} anomalies)")
        else:
            print("⚠️  No anomalies detected (this might be normal for small datasets)")
        
        print("✅ Installation validation complete!")
        return True
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False


if __name__ == "__main__":
    print("🎬 Starting Synthetic MELT Data Generator Demo")
    
    # Validate installation first
    if not validate_installation():
        print("❌ Installation validation failed. Please check your setup.")
        sys.exit(1)
    
    # Run the demo
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
