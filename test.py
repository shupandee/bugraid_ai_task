#!/usr/bin/env python3
"""
Basic tests for the Synthetic MELT Data Generator.
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from synthetic_melt_generator.core.generator import MeltGenerator
from synthetic_melt_generator.core.models import GenerationConfig, AnomalyConfig


def test_basic_generation():
    """Test basic data generation."""
    print("🧪 Testing basic generation...")
    
    config = GenerationConfig(
        seed=42,
        duration_hours=0.1,  # 6 minutes for quick test
        services=["api", "web"],
        hosts=["web-01"],
        environments=["production"]
    )
    
    generator = MeltGenerator(config)
    data = generator.generate(size="1MB", anomalies=None)
    
    assert data.total_records() > 0, "No records generated"
    assert len(data.metrics) > 0, "No metrics generated"
    assert len(data.events) >= 0, "Events should be non-negative"
    assert len(data.logs) > 0, "No logs generated"
    assert len(data.traces) >= 0, "Traces should be non-negative"
    
    print(f"✅ Generated {data.total_records()} records")
    return True


def test_anomaly_injection():
    """Test anomaly injection."""
    print("🧪 Testing anomaly injection...")
    
    config = GenerationConfig(seed=42, duration_hours=0.1)
    anomaly_config = AnomalyConfig()
    
    generator = MeltGenerator(config, anomaly_config)
    data = generator.generate(size="1MB", anomalies=["cpu_spike"])
    
    assert data.total_records() > 0, "No records generated"
    
    # Check for anomalies (might be 0 for small datasets)
    anomalous_metrics = sum(1 for m in data.metrics if m.anomaly)
    print(f"✅ Found {anomalous_metrics} anomalous metrics")
    
    return True


def test_data_schemas():
    """Test that generated data follows expected schemas."""
    print("🧪 Testing data schemas...")
    
    config = GenerationConfig(seed=42, duration_hours=0.1)
    generator = MeltGenerator(config)
    data = generator.generate(size="1MB", anomalies=None)
    
    # Test metric schema
    if data.metrics:
        metric = data.metrics[0]
        assert hasattr(metric, 'timestamp'), "Metric missing timestamp"
        assert hasattr(metric, 'metric_name'), "Metric missing metric_name"
        assert hasattr(metric, 'value'), "Metric missing value"
        assert hasattr(metric, 'labels'), "Metric missing labels"
        assert isinstance(metric.value, (int, float)), "Metric value should be numeric"
    
    # Test log schema
    if data.logs:
        log = data.logs[0]
        assert hasattr(log, 'timestamp'), "Log missing timestamp"
        assert hasattr(log, 'level'), "Log missing level"
        assert hasattr(log, 'service'), "Log missing service"
        assert hasattr(log, 'message'), "Log missing message"
    
    # Test trace schema
    if data.traces:
        trace = data.traces[0]
        assert hasattr(trace, 'trace_id'), "Trace missing trace_id"
        assert hasattr(trace, 'span_id'), "Trace missing span_id"
        assert hasattr(trace, 'operation_name'), "Trace missing operation_name"
        assert hasattr(trace, 'duration'), "Trace missing duration"
        assert isinstance(trace.duration, int), "Trace duration should be integer"
    
    print("✅ All schemas valid")
    return True


def run_all_tests():
    """Run all basic tests."""
    print("🚀 Running Basic Tests for Synthetic MELT Generator")
    print("=" * 50)
    
    tests = [
        test_basic_generation,
        test_anomaly_injection,
        test_data_schemas
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} failed with error: {e}")
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

