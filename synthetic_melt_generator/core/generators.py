"""
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
                    f.write(json.dumps(metric_dict) + "\n")
        
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
                    f.write(json.dumps(log_dict) + "\n")
        
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
                    f.write(json.dumps(trace_dict) + "\n")
        
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
                    f.write(json.dumps(event_dict) + "\n")
        
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
        
        # Create statistics file - FIXED: Calculate output size safely
        statistics = {
            "total_records": data.total_records(),
            "metrics_count": len(data.metrics),
            "logs_count": len(data.logs), 
            "traces_count": len(data.traces),
            "events_count": len(data.events),
        }
        
        # Calculate output size safely
        total_size = 0
        for jsonl_file in output_path.glob("*.jsonl"):
            if jsonl_file.exists():
                total_size += jsonl_file.stat().st_size
        
        statistics["output_size_mb"] = total_size / (1024 * 1024)
        
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