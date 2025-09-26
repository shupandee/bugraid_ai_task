#!/usr/bin/env python3
"""
Script to create the missing package structure for synthetic_melt_generator
"""

import os
from pathlib import Path

def create_package_structure():
    """Create the missing package directories and files."""
    
    # Base package directory
    pkg_dir = Path("synthetic_melt_generator")
    
    # Create all necessary directories
    directories = [
        pkg_dir,
        pkg_dir / "core",
        pkg_dir / "generators", 
        pkg_dir / "anomalies",
        pkg_dir / "validation",
        pkg_dir / "benchmarks"
    ]
    
    for directory in directories:
        directory.mkdir(exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Create __init__.py files
    init_files = [
        (pkg_dir / "__init__.py", '''"""
Synthetic MELT Data Generator

A comprehensive synthetic data generator for MELT (Metrics, Events, Logs, Traces) data
designed for testing anomaly detection and Root Cause Analysis (RCA) systems.
"""

__version__ = "1.0.0"
__author__ = "BugRaid AI Assessment"

from .core.generator import MeltGenerator
from .core.models import GenerationConfig, AnomalyConfig

__all__ = [
    "MeltGenerator",
    "GenerationConfig", 
    "AnomalyConfig"
]
'''),
        
        (pkg_dir / "core" / "__init__.py", ''),
        (pkg_dir / "generators" / "__init__.py", ''),
        (pkg_dir / "anomalies" / "__init__.py", ''),
        (pkg_dir / "validation" / "__init__.py", ''),
        (pkg_dir / "benchmarks" / "__init__.py", ''),
    ]
    
    for file_path, content in init_files:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created file: {file_path}")

def create_core_models():
    """Create the core models file."""
    
    models_content = '''"""
Core data models for the synthetic MELT generator.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class LogLevel(Enum):
    """Log severity levels."""
    DEBUG = "DEBUG"
    INFO = "INFO" 
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class EventSeverity(Enum):
    """Event severity levels."""
    debug = "debug"
    info = "info"
    warn = "warn"
    error = "error"
    critical = "critical"


@dataclass
class Metric:
    """A single metric data point."""
    timestamp: str
    metric_name: str
    value: float
    labels: Dict[str, str]
    anomaly: bool = False


@dataclass  
class Event:
    """A single event record."""
    timestamp: str
    event_type: str
    severity: EventSeverity
    source: str
    message: str
    metadata: Dict[str, Any]


@dataclass
class Log:
    """A single log entry."""
    timestamp: str
    level: LogLevel
    service: str
    message: str
    metadata: Dict[str, Any]
    trace_id: Optional[str] = None
    span_id: Optional[str] = None


@dataclass
class Trace:
    """A single trace span."""
    trace_id: str
    span_id: str
    operation_name: str
    start_time: str
    duration: int  # microseconds
    service: str
    tags: Dict[str, str]
    status: str = "ok"
    parent_span_id: Optional[str] = None


@dataclass
class MeltData:
    """Container for all generated MELT data."""
    metrics: List[Metric] = field(default_factory=list)
    events: List[Event] = field(default_factory=list)
    logs: List[Log] = field(default_factory=list)
    traces: List[Trace] = field(default_factory=list)
    
    def total_records(self) -> int:
        """Return total number of records across all data types."""
        return len(self.metrics) + len(self.events) + len(self.logs) + len(self.traces)


@dataclass
class GenerationConfig:
    """Configuration for data generation."""
    seed: int = 42
    duration_hours: float = 24
    services: List[str] = field(default_factory=lambda: ["api", "web", "database", "cache"])
    hosts: List[str] = field(default_factory=lambda: ["web-01", "web-02", "db-01", "cache-01"])
    environments: List[str] = field(default_factory=lambda: ["production", "staging"])
    metrics_frequency_seconds: int = 30
    logs_frequency_seconds: int = 1
    traces_frequency_seconds: int = 10
    events_frequency_seconds: int = 300
    error_rate: float = 0.05
    debug_log_ratio: float = 0.3
    missing_span_rate: float = 0.02
    max_trace_depth: int = 5
    incident_probability: float = 0.1


@dataclass
class AnomalyConfig:
    """Configuration for anomaly injection."""
    cpu_spike_probability: float = 0.05
    cpu_spike_duration_minutes: int = 5
    cpu_spike_intensity: float = 3.0
    
    service_outage_probability: float = 0.01
    service_outage_duration_minutes: int = 10
    service_outage_services: List[str] = field(default_factory=lambda: ["api", "database"])
    
    latency_spike_probability: float = 0.03
    latency_spike_duration_minutes: int = 3
    latency_spike_multiplier: float = 5.0
    
    error_burst_probability: float = 0.02
    error_burst_duration_minutes: int = 2
    error_burst_rate: float = 0.5
'''
    
    models_file = Path("synthetic_melt_generator/core/models.py")
    with open(models_file, 'w', encoding='utf-8') as f:
        f.write(models_content)
    print(f"Created file: {models_file}")


def create_core_generator():
    """Create the core generator file."""
    
    generator_content = '''"""
Core MELT data generator.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any
import uuid

from .models import (
    MeltData, Metric, Event, Log, Trace,
    GenerationConfig, AnomalyConfig,
    LogLevel, EventSeverity
)


class MeltGenerator:
    """Main generator for MELT data."""
    
    def __init__(self, config: Optional[GenerationConfig] = None, 
                 anomaly_config: Optional[AnomalyConfig] = None):
        self.config = config or GenerationConfig()
        self.anomaly_config = anomaly_config or AnomalyConfig()
        
        # Set random seed for reproducibility
        random.seed(self.config.seed)
        
        # Message templates for logs
        self.log_messages = [
            "Request processed successfully",
            "Database connection established",
            "User authentication completed", 
            "Cache operation completed",
            "Background job started",
            "Configuration updated",
            "Health check passed",
            "Request timeout occurred",
            "Database connection failed",
            "Authentication failed",
            "Cache miss occurred",
            "Job execution failed",
            "Configuration validation error",
            "Health check failed"
        ]
        
        # Event templates
        self.event_templates = [
            ("deployment", "info", "ci-cd-pipeline", "Service {service} version {version} deployed"),
            ("scaling", "info", "autoscaler", "Scaled {service} from {old} to {new} instances"),
            ("alert", "warn", "monitoring", "High {metric} detected on {service}"),
            ("incident", "error", "monitoring", "Service {service} experiencing issues"),
            ("maintenance", "info", "ops-team", "Maintenance window started for {service}")
        ]
    
    def generate(self, size: str, anomalies: Optional[List[str]] = None) -> MeltData:
        """Generate MELT data of specified size."""
        
        # Parse target size
        target_bytes = self._parse_size(size)
        
        # Calculate approximate record counts based on average sizes
        # These are rough estimates: metric ~200 bytes, log ~300 bytes, etc.
        total_target_records = target_bytes // 250  # Average record size
        
        # Distribute records across data types
        metrics_count = int(total_target_records * 0.4)  # 40% metrics
        logs_count = int(total_target_records * 0.35)    # 35% logs  
        traces_count = int(total_target_records * 0.15)  # 15% traces
        events_count = int(total_target_records * 0.1)   # 10% events
        
        print(f"Generating approximately {total_target_records:,} records...")
        print(f"  Metrics: {metrics_count:,}")
        print(f"  Logs: {logs_count:,}")
        print(f"  Traces: {traces_count:,}")
        print(f"  Events: {events_count:,}")
        
        # Generate data
        data = MeltData()
        
        if metrics_count > 0:
            data.metrics = self._generate_metrics(metrics_count, anomalies)
        
        if logs_count > 0:
            data.logs = self._generate_logs(logs_count, anomalies)
            
        if traces_count > 0:
            data.traces = self._generate_traces(traces_count, anomalies)
            
        if events_count > 0:
            data.events = self._generate_events(events_count, anomalies)
        
        return data
    
    def _parse_size(self, size: str) -> int:
        """Parse size string like '1GB', '100MB' to bytes."""
        size = size.upper()
        
        if size.endswith('GB'):
            return int(float(size[:-2]) * 1024 * 1024 * 1024)
        elif size.endswith('MB'): 
            return int(float(size[:-2]) * 1024 * 1024)
        elif size.endswith('KB'):
            return int(float(size[:-2]) * 1024)
        else:
            return int(size)  # Assume bytes
    
    def _generate_metrics(self, count: int, anomalies: Optional[List[str]]) -> List[Metric]:
        """Generate synthetic metrics."""
        metrics = []
        base_time = datetime.now()
        
        # Metric types with their ranges
        metric_types = [
            ("cpu_usage", "percent", 5, 80, 95),      # min, normal_max, spike_max
            ("memory_usage", "percent", 10, 75, 95),
            ("disk_usage", "percent", 20, 85, 98),
            ("response_time", "ms", 10, 200, 2000),
            ("request_rate", "req/s", 1, 100, 500),
            ("error_rate", "percent", 0, 5, 25)
        ]
        
        should_inject_cpu_spike = anomalies and "cpu_spike" in anomalies
        cpu_spike_start = random.randint(count // 4, count // 2) if should_inject_cpu_spike else -1
        cpu_spike_duration = 20  # records
        
        for i in range(count):
            # Time progression
            timestamp = base_time + timedelta(seconds=i * self.config.metrics_frequency_seconds)
            
            # Choose metric type and service
            metric_name, unit, min_val, normal_max, spike_max = random.choice(metric_types)
            service = random.choice(self.config.services)
            host = random.choice(self.config.hosts)
            
            # Determine if this is an anomalous point
            is_anomaly = False
            if (should_inject_cpu_spike and metric_name == "cpu_usage" and 
                cpu_spike_start <= i < cpu_spike_start + cpu_spike_duration):
                # CPU spike anomaly
                value = random.uniform(spike_max - 10, spike_max)
                is_anomaly = True
            else:
                # Normal value with some natural variation
                base_value = random.uniform(min_val, normal_max)
                # Add some realistic noise
                noise = random.uniform(-0.1, 0.1) * base_value
                value = max(min_val, base_value + noise)
            
            metric = Metric(
                timestamp=timestamp.isoformat() + "Z",
                metric_name=metric_name,
                value=round(value, 2),
                labels={
                    "service": service,
                    "host": host,
                    "environment": random.choice(self.config.environments),
                    "unit": unit
                },
                anomaly=is_anomaly
            )
            
            metrics.append(metric)
        
        return metrics
    
    def _generate_logs(self, count: int, anomalies: Optional[List[str]]) -> List[Log]:
        """Generate synthetic logs."""
        logs = []
        base_time = datetime.now()
        
        # Log level distribution (more info/debug, fewer errors)
        level_weights = [
            (LogLevel.DEBUG, 30),
            (LogLevel.INFO, 50), 
            (LogLevel.WARN, 15),
            (LogLevel.ERROR, 4),
            (LogLevel.CRITICAL, 1)
        ]
        
        should_inject_errors = anomalies and "error_burst" in anomalies
        error_burst_start = random.randint(count // 4, count // 2) if should_inject_errors else -1
        error_burst_duration = 50  # records
        
        for i in range(count):
            timestamp = base_time + timedelta(seconds=i * self.config.logs_frequency_seconds)
            service = random.choice(self.config.services)
            
            # Choose log level
            if (should_inject_errors and 
                error_burst_start <= i < error_burst_start + error_burst_duration):
                # Error burst - much higher chance of errors
                level = random.choice([LogLevel.ERROR, LogLevel.CRITICAL, LogLevel.WARN])
            else:
                # Normal distribution
                level = random.choices([l[0] for l in level_weights], 
                                     weights=[l[1] for l in level_weights])[0]
            
            # Choose appropriate message based on log level
            if level in [LogLevel.ERROR, LogLevel.CRITICAL]:
                message = random.choice([
                    "Database connection failed",
                    "Authentication failed for user", 
                    "Request timeout occurred",
                    "Job execution failed",
                    "Configuration validation error",
                    "Health check failed"
                ])
            else:
                message = random.choice(self.log_messages[:7])  # Normal messages
            
            log = Log(
                timestamp=timestamp.isoformat() + "Z",
                level=level,
                service=service,
                message=message,
                metadata={
                    "service": service,
                    "host": random.choice(self.config.hosts),
                    "environment": random.choice(self.config.environments),
                    "version": f"v{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
                    "thread_id": random.randint(1, 100),
                    "process_id": random.randint(1000, 9999)
                },
                trace_id=self._generate_trace_id() if random.random() < 0.7 else None,
                span_id=self._generate_span_id() if random.random() < 0.7 else None
            )
            
            logs.append(log)
        
        return logs
    
    def _generate_traces(self, count: int, anomalies: Optional[List[str]]) -> List[Trace]:
        """Generate synthetic traces."""
        traces = []
        base_time = datetime.now()
        
        operations = [
            "http_request", "database_query", "cache_operation",
            "message_processing", "file_operation", "external_api_call"
        ]
        
        should_inject_latency = anomalies and "latency_spike" in anomalies
        latency_spike_start = random.randint(count // 4, count // 2) if should_inject_latency else -1
        latency_spike_duration = 15  # records
        
        for i in range(count):
            timestamp = base_time + timedelta(seconds=i * self.config.traces_frequency_seconds)
            service = random.choice(self.config.services)
            operation = random.choice(operations)
            
            # Generate trace duration
            if (should_inject_latency and 
                latency_spike_start <= i < latency_spike_start + latency_spike_duration):
                # Latency spike - much slower
                duration = random.randint(500000, 2000000)  # 500ms - 2s in microseconds
                status = "timeout" if duration > 1500000 else "ok"
            else:
                # Normal duration
                duration = random.randint(1000, 100000)  # 1ms - 100ms in microseconds
                status = "error" if random.random() < 0.02 else "ok"
            
            trace = Trace(
                trace_id=self._generate_trace_id(),
                span_id=self._generate_span_id(),
                operation_name=operation,
                start_time=timestamp.isoformat() + "Z",
                duration=duration,
                service=service,
                tags={
                    "service.name": service,
                    "service.version": f"v{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
                    "environment": random.choice(self.config.environments),
                    "host.name": random.choice(self.config.hosts)
                },
                status=status,
                parent_span_id=self._generate_span_id() if random.random() < 0.3 else None
            )
            
            traces.append(trace)
        
        return traces
    
    def _generate_events(self, count: int, anomalies: Optional[List[str]]) -> List[Event]:
        """Generate synthetic events."""
        events = []
        base_time = datetime.now()
        
        for i in range(count):
            timestamp = base_time + timedelta(seconds=i * self.config.events_frequency_seconds)
            
            # Choose event template
            event_type, severity, source, message_template = random.choice(self.event_templates)
            service = random.choice(self.config.services)
            
            # Fill in message template
            message = message_template.format(
                service=service,
                version=f"v{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
                old=random.randint(1, 5),
                new=random.randint(1, 10),
                metric="CPU" if random.random() < 0.5 else "memory"
            )
            
            event = Event(
                timestamp=timestamp.isoformat() + "Z",
                event_type=event_type,
                severity=EventSeverity(severity),
                source=source,
                message=message,
                metadata={
                    "service": service,
                    "host": random.choice(self.config.hosts),
                    "environment": random.choice(self.config.environments),
                    "event_id": f"evt_{uuid.uuid4().hex[:8]}",
                    "correlation_id": f"corr_{uuid.uuid4().hex[:8]}"
                }
            )
            
            events.append(event)
        
        return events
    
    def _generate_trace_id(self) -> str:
        """Generate a random trace ID."""
        return uuid.uuid4().hex[:16]
    
    def _generate_span_id(self) -> str:
        """Generate a random span ID."""
        return uuid.uuid4().hex[:8]
    
    def save(self, data: MeltData, output_dir: str):
        """Save generated data to files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save each data type to separate JSONL files
        if data.metrics:
            with open(output_path / "metrics.jsonl", 'w') as f:
                for metric in data.metrics:
                    # Convert to dict for JSON serialization
                    metric_dict = {
                        "timestamp": metric.timestamp,
                        "metric_name": metric.metric_name,
                        "value": metric.value,
                        "labels": metric.labels,
                        "anomaly": metric.anomaly
                    }
                    f.write(json.dumps(metric_dict) + "\\n")
        
        if data.logs:
            with open(output_path / "logs.jsonl", 'w') as f:
                for log in data.logs:
                    log_dict = {
                        "timestamp": log.timestamp,
                        "level": log.level.value,
                        "service": log.service,
                        "message": log.message,
                        "metadata": log.metadata,
                        "trace_id": log.trace_id,
                        "span_id": log.span_id
                    }
                    f.write(json.dumps(log_dict) + "\\n")
        
        if data.traces:
            with open(output_path / "traces.jsonl", 'w') as f:
                for trace in data.traces:
                    trace_dict = {
                        "trace_id": trace.trace_id,
                        "span_id": trace.span_id,
                        "parent_span_id": trace.parent_span_id,
                        "operation_name": trace.operation_name,
                        "start_time": trace.start_time,
                        "duration": trace.duration,
                        "service": trace.service,
                        "tags": trace.tags,
                        "status": trace.status
                    }
                    f.write(json.dumps(trace_dict) + "\\n")
        
        if data.events:
            with open(output_path / "events.jsonl", 'w') as f:
                for event in data.events:
                    event_dict = {
                        "timestamp": event.timestamp,
                        "event_type": event.event_type,
                        "severity": event.severity.value,
                        "source": event.source,
                        "message": event.message,
                        "metadata": event.metadata
                    }
                    f.write(json.dumps(event_dict) + "\\n")
        
        # Create metadata file
        metadata = {
            "generated_at": datetime.now().isoformat() + "Z",
            "generator_version": "1.0.0",
            "data_types": [],
            "generation_config": {
                "seed": self.config.seed,
                "duration_hours": self.config.duration_hours,
                "services": self.config.services,
                "environments": self.config.environments
            }
        }
        
        if data.metrics:
            metadata["data_types"].append("metrics")
        if data.logs:
            metadata["data_types"].append("logs")
        if data.traces:
            metadata["data_types"].append("traces")
        if data.events:
            metadata["data_types"].append("events")
        
        with open(output_path / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Create statistics file
        statistics = {
            "total_records": data.total_records(),
            "metrics_count": len(data.metrics),
            "logs_count": len(data.logs), 
            "traces_count": len(data.traces),
            "events_count": len(data.events),
            "output_size_mb": sum((output_path / f).stat().st_size for f in output_path.glob("*.jsonl")) / (1024 * 1024)
        }
        
        with open(output_path / "statistics.json", 'w') as f:
            json.dump(statistics, f, indent=2)
        
        print(f"Data saved to {output_path}")
        print(f"  Total records: {data.total_records():,}")
        if data.metrics:
            print(f"  metrics.jsonl: {len(data.metrics):,} records")
        if data.logs:
            print(f"  logs.jsonl: {len(data.logs):,} records")
        if data.traces:
            print(f"  traces.jsonl: {len(data.traces):,} records")
        if data.events:
            print(f"  events.jsonl: {len(data.events):,} records")
'''
    
    generator_file = Path("synthetic_melt_generator/core/generator.py")
    with open(generator_file, 'w', encoding='utf-8') as f:
        f.write(generator_content)
    print(f"Created file: {generator_file}")


def main():
    """Main function to create the package structure."""
    print("Creating synthetic_melt_generator package structure...")
    
    create_package_structure()
    create_core_models()
    create_core_generator()
    
    print("\n✅ Package structure created successfully!")
    print("\nNext steps:")
    print("1. Test the package: python -c \"from synthetic_melt_generator import MeltGenerator; print('Import successful!')\"")
    print("2. Run the demo: python simple_demo.py")
    print("3. Generate data: python -c \"from synthetic_melt_generator import *; g = MeltGenerator(); d = g.generate('1MB'); g.save(d, './test_output')\"")


if __name__ == "__main__":
    main()