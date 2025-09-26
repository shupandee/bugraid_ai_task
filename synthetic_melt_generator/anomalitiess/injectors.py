"""
Anomaly injection system for MELT data.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

from ..core.models import AnomalyConfig, MeltData, LogLevel, TraceStatus


class AnomalyInjector:
    """Injects anomalies into generated MELT data."""
    
    def __init__(self, config: AnomalyConfig):
        self.config = config
    
    def inject_anomalies(self, data: MeltData, anomaly_types: List[str]) -> MeltData:
        """Inject specified anomalies into the data."""
        print(f"Injecting anomalies: {anomaly_types}")
        
        for anomaly_type in anomaly_types:
            if anomaly_type == "all":
                # Inject all available anomaly types
                self._inject_cpu_spike(data)
                self._inject_service_outage(data)
                self._inject_latency_spike(data)
                self._inject_error_burst(data)
            elif anomaly_type == "cpu_spike":
                self._inject_cpu_spike(data)
            elif anomaly_type == "service_outage":
                self._inject_service_outage(data)
            elif anomaly_type == "latency_spike":
                self._inject_latency_spike(data)
            elif anomaly_type == "error_burst":
                self._inject_error_burst(data)
        
        return data
    
    def _inject_cpu_spike(self, data: MeltData):
        """Inject CPU usage spikes."""
        config = self.config.cpu_spike
        probability = config.get("probability", 0.05)
        intensity = config.get("intensity", 3.0)
        duration_minutes = config.get("duration_minutes", 5)
        
        cpu_metrics = [m for m in data.metrics if m.metric_name == "cpu_usage"]
        if not cpu_metrics:
            return
        
        # Select random time windows for spikes
        spike_count = int(len(cpu_metrics) * probability)
        spike_metrics = random.sample(cpu_metrics, min(spike_count, len(cpu_metrics)))
        
        for metric in spike_metrics:
            # Find nearby metrics within the duration window
            start_time = metric.timestamp
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            nearby_metrics = [
                m for m in cpu_metrics 
                if start_time <= m.timestamp <= end_time and m.labels.get("host") == metric.labels.get("host")
            ]
            
            # Apply spike to nearby metrics
            for nearby_metric in nearby_metrics:
                nearby_metric.value = min(100.0, nearby_metric.value * intensity)
                nearby_metric.anomaly = True
        
        print(f"Injected CPU spikes in {spike_count} time windows")
    
    def _inject_service_outage(self, data: MeltData):
        """Inject service outage patterns."""
        config = self.config.service_outage
        probability = config.get("probability", 0.01)
        duration_minutes = config.get("duration_minutes", 10)
        affected_services = config.get("affected_services", ["api", "database"])
        
        # Select services to affect
        services_to_affect = random.sample(affected_services, random.randint(1, len(affected_services)))
        
        if not data.metrics:
            return
        
        # Find random time window for outage
        if len(data.metrics) == 0:
            return
            
        start_metric = random.choice(data.metrics)
        start_time = start_metric.timestamp
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        outage_applied = False
        
        for service in services_to_affect:
            if random.random() > probability:
                continue
                
            outage_applied = True
            
            # Affect metrics
            affected_metrics = [
                m for m in data.metrics 
                if (start_time <= m.timestamp <= end_time and 
                    m.labels.get("service") == service)
            ]
            
            for metric in affected_metrics:
                if metric.metric_name == "cpu_usage":
                    metric.value = max(0, metric.value * 0.1)  # Very low CPU during outage
                elif metric.metric_name == "error_rate":
                    metric.value = min(1.0, metric.value * 10)  # High error rate
                elif metric.metric_name == "response_time":
                    metric.value = metric.value * 20  # Very slow responses
                metric.anomaly = True
            
            # Affect logs
            affected_logs = [
                l for l in data.logs
                if (start_time <= l.timestamp <= end_time and l.service == service)
            ]
            
            for log in affected_logs:
                if random.random() < 0.7:  # 70% of logs become errors
                    log.level = LogLevel.ERROR
                    log.message = f"Service {service} is unavailable - " + log.message
            
            # Affect traces
            affected_traces = [
                t for t in data.traces
                if (start_time <= t.start_time <= end_time and t.service == service)
            ]
            
            for trace in affected_traces:
                if random.random() < 0.8:  # 80% of traces fail
                    trace.status = TraceStatus.ERROR
                    trace.duration = trace.duration * 3  # Much slower
        
        if outage_applied:
            print(f"Injected service outage for {services_to_affect} from {start_time} to {end_time}")
    
    def _inject_latency_spike(self, data: MeltData):
        """Inject response time spikes."""
        config = self.config.latency_spike
        probability = config.get("probability", 0.03)
        multiplier = config.get("multiplier", 5.0)
        duration_minutes = config.get("duration_minutes", 3)
        
        response_time_metrics = [m for m in data.metrics if m.metric_name == "response_time"]
        if not response_time_metrics:
            return
        
        # Select random metrics for latency spikes
        spike_count = int(len(response_time_metrics) * probability)
        spike_metrics = random.sample(response_time_metrics, min(spike_count, len(response_time_metrics)))
        
        for metric in spike_metrics:
            start_time = metric.timestamp
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            # Apply to nearby response time metrics
            nearby_metrics = [
                m for m in response_time_metrics
                if (start_time <= m.timestamp <= end_time and 
                    m.labels.get("service") == metric.labels.get("service"))
            ]
            
            for nearby_metric in nearby_metrics:
                nearby_metric.value = nearby_metric.value * multiplier
                nearby_metric.anomaly = True
            
            # Also affect related traces
            related_traces = [
                t for t in data.traces
                if (start_time <= t.start_time <= end_time and 
                    t.service == metric.labels.get("service"))
            ]
            
            for trace in related_traces:
                trace.duration = int(trace.duration * multiplier)
                if trace.duration > 1000000:  # > 1 second
                    trace.status = TraceStatus.TIMEOUT
        
        print(f"Injected latency spikes in {spike_count} time windows")
    
    def _inject_error_burst(self, data: MeltData):
        """Inject error rate bursts."""
        config = self.config.error_burst
        probability = config.get("probability", 0.02)
        error_rate = config.get("error_rate", 0.5)
        duration_minutes = config.get("duration_minutes", 2)
        
        error_rate_metrics = [m for m in data.metrics if m.metric_name == "error_rate"]
        if not error_rate_metrics:
            return
        
        # Select random time windows for error bursts
        burst_count = int(len(error_rate_metrics) * probability)
        burst_metrics = random.sample(error_rate_metrics, min(burst_count, len(error_rate_metrics)))
        
        for metric in burst_metrics:
            start_time = metric.timestamp
            end_time = start_time + timedelta(minutes=duration_minutes)
            service = metric.labels.get("service")
            
            # Apply to error rate metrics
            nearby_error_metrics = [
                m for m in error_rate_metrics
                if (start_time <= m.timestamp <= end_time and 
                    m.labels.get("service") == service)
            ]
            
            for nearby_metric in nearby_error_metrics:
                nearby_metric.value = min(1.0, error_rate)
                nearby_metric.anomaly = True
            
            # Generate more error logs
            service_logs = [
                l for l in data.logs
                if (start_time <= l.timestamp <= end_time and l.service == service)
            ]
            
            for log in service_logs:
                if random.random() < error_rate:
                    log.level = LogLevel.ERROR
                    log.message = "Error burst: " + log.message
            
            # Affect traces
            service_traces = [
                t for t in data.traces
                if (start_time <= t.start_time <= end_time and t.service == service)
            ]
            
            for trace in service_traces:
                if random.random() < error_rate:
                    trace.status = TraceStatus.ERROR
        
        print(f"Injected error bursts in {burst_count} time windows")