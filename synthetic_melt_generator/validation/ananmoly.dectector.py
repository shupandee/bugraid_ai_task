"""
Anomaly detector for testing synthetic MELT data.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class AnomalyDetector:
    """Simple anomaly detector for testing generated data."""
    
    def __init__(self):
        self.thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 90.0,
            "response_time": 1000.0,
            "error_rate": 0.1
        }
    
    def detect_anomalies(self, data_dir: str) -> Dict[str, Any]:
        """Detect anomalies in generated MELT data."""
        data_path = Path(data_dir)
        
        report = {
            "summary": {
                "total_anomalies": 0,
                "cpu_spikes": 0,
                "latency_spikes": 0,
                "error_bursts": 0,
                "service_outages": 0
            },
            "details": {
                "metrics": [],
                "logs": [],
                "traces": [],
                "events": []
            }
        }
        
        # Analyze metrics
        metrics_file = data_path / "metrics.jsonl"
        if metrics_file.exists():
            metrics_anomalies = self._detect_metrics_anomalies(metrics_file)
            report["details"]["metrics"] = metrics_anomalies
            report["summary"]["cpu_spikes"] += len([a for a in metrics_anomalies if a["type"] == "cpu_spike"])
            report["summary"]["latency_spikes"] += len([a for a in metrics_anomalies if a["type"] == "latency_spike"])
        
        # Analyze logs
        logs_file = data_path / "logs.jsonl"
        if logs_file.exists():
            log_anomalies = self._detect_log_anomalies(logs_file)
            report["details"]["logs"] = log_anomalies
            report["summary"]["error_bursts"] += len([a for a in log_anomalies if a["type"] == "error_burst"])
        
        # Analyze traces
        traces_file = data_path / "traces.jsonl"
        if traces_file.exists():
            trace_anomalies = self._detect_trace_anomalies(traces_file)
            report["details"]["traces"] = trace_anomalies
            report["summary"]["latency_spikes"] += len([a for a in trace_anomalies if a["type"] == "latency_spike"])
        
        # Analyze events
        events_file = data_path / "events.jsonl"
        if events_file.exists():
            event_anomalies = self._detect_event_anomalies(events_file)
            report["details"]["events"] = event_anomalies
            report["summary"]["service_outages"] += len([a for a in event_anomalies if a["type"] == "service_outage"])
        
        # Calculate total
        report["summary"]["total_anomalies"] = (
            report["summary"]["cpu_spikes"] +
            report["summary"]["latency_spikes"] +
            report["summary"]["error_bursts"] +
            report["summary"]["service_outages"]
        )
        
        return report
    
    def _detect_metrics_anomalies(self, file_path: Path) -> List[Dict[str, Any]]:
        """Detect anomalies in metrics data."""
        anomalies = []
        
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    
                    # Check for marked anomalies
                    if record.get("anomaly", False):
                        anomaly_type = "unknown"
                        if "cpu" in record["metric_name"]:
                            anomaly_type = "cpu_spike"
                        elif "response_time" in record["metric_name"]:
                            anomaly_type = "latency_spike"
                        elif "error_rate" in record["metric_name"]:
                            anomaly_type = "error_burst"
                        
                        anomalies.append({
                            "type": anomaly_type,
                            "timestamp": record["timestamp"],
                            "metric": record["metric_name"],
                            "value": record["value"],
                            "service": record["labels"].get("service", "unknown")
                        })
                    
                    # Check threshold-based anomalies
                    metric_name = record["metric_name"]
                    value = record["value"]
                    
                    if metric_name in self.thresholds and value > self.thresholds[metric_name]:
                        anomaly_type = "threshold_exceeded"
                        if "cpu" in metric_name:
                            anomaly_type = "cpu_spike"
                        elif "response_time" in metric_name:
                            anomaly_type = "latency_spike"
                        
                        anomalies.append({
                            "type": anomaly_type,
                            "timestamp": record["timestamp"],
                            "metric": metric_name,
                            "value": value,
                            "threshold": self.thresholds[metric_name],
                            "service": record["labels"].get("service", "unknown")
                        })
        
        return anomalies
    
    def _detect_log_anomalies(self, file_path: Path) -> List[Dict[str, Any]]:
        """Detect anomalies in log data."""
        anomalies = []
        error_count = 0
        total_count = 0
        
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    total_count += 1
                    
                    # Count error logs
                    if record["level"] in ["ERROR", "CRITICAL"]:
                        error_count += 1
                    
                    # Check for error burst markers
                    if record.get("metadata", {}).get("error_burst"):
                        anomalies.append({
                            "type": "error_burst",
                            "timestamp": record["timestamp"],
                            "level": record["level"],
                            "service": record["service"],
                            "message": record["message"][:100]
                        })
        
        # Check overall error rate
        if total_count > 0:
            error_rate = error_count / total_count
            if error_rate > 0.1:  # 10% error rate threshold
                anomalies.append({
                    "type": "high_error_rate",
                    "error_rate": error_rate,
                    "error_count": error_count,
                    "total_count": total_count
                })
        
        return anomalies
    
    def _detect_trace_anomalies(self, file_path: Path) -> List[Dict[str, Any]]:
        """Detect anomalies in trace data."""
        anomalies = []
        
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    
                    # Check for failed traces
                    if record["status"] in ["error", "timeout"]:
                        anomalies.append({
                            "type": "trace_failure",
                            "timestamp": record["start_time"],
                            "trace_id": record["trace_id"],
                            "operation": record["operation_name"],
                            "status": record["status"],
                            "service": record["service"]
                        })
                    
                    # Check for latency spikes
                    duration_ms = record["duration"] / 1000  # Convert to milliseconds
                    if duration_ms > 1000:  # 1 second threshold
                        anomalies.append({
                            "type": "latency_spike",
                            "timestamp": record["start_time"],
                            "trace_id": record["trace_id"],
                            "operation": record["operation_name"],
                            "duration_ms": duration_ms,
                            "service": record["service"]
                        })
                    
                    # Check for latency spike markers
                    if record.get("tags", {}).get("latency_spike"):
                        anomalies.append({
                            "type": "latency_spike",
                            "timestamp": record["start_time"],
                            "trace_id": record["trace_id"],
                            "operation": record["operation_name"],
                            "duration_ms": record["duration"] / 1000,
                            "service": record["service"],
                            "marked": True
                        })
        
        return anomalies
    
    def _detect_event_anomalies(self, file_path: Path) -> List[Dict[str, Any]]:
        """Detect anomalies in event data."""
        anomalies = []
        
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    
                    # Check for incident events
                    if record["event_type"] == "incident":
                        anomaly_type = "incident"
                        if "outage" in record["message"].lower():
                            anomaly_type = "service_outage"
                        
                        anomalies.append({
                            "type": anomaly_type,
                            "timestamp": record["timestamp"],
                            "severity": record["severity"],
                            "message": record["message"],
                            "service": record["metadata"].get("service", "unknown")
                        })
                    
                    # Check for critical alerts
                    if record["event_type"] == "alert" and record["severity"] == "critical":
                        anomalies.append({
                            "type": "critical_alert",
                            "timestamp": record["timestamp"],
                            "message": record["message"],
                            "service": record["metadata"].get("service", "unknown")
                        })
        
        return anomalies
