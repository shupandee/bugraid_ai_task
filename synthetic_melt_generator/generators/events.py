"""
Generator for synthetic events data.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any

from ..core.models import GenerationConfig, EventRecord, EventSeverity


class EventsGenerator:
    """Generator for operational events."""
    
    def __init__(self, config: GenerationConfig):
        self.config = config
        self.event_types = [
            "deployment", "scaling", "alert", "incident", "maintenance",
            "security", "backup", "configuration", "network", "performance"
        ]
        self.sources = [
            "ci-cd-pipeline", "monitoring-system", "auto-scaler", 
            "security-scanner", "backup-service", "load-balancer"
        ]
    
    def generate_batch(self, timestamp: datetime, count: int) -> List[EventRecord]:
        """Generate a batch of events."""
        events = []
        
        for _ in range(count):
            event_type = random.choice(self.event_types)
            severity = self._choose_severity(event_type)
            source = random.choice(self.sources)
            service = random.choice(self.config.services)
            host = random.choice(self.config.hosts)
            environment = random.choice(self.config.environments)
            
            message = self._generate_message(event_type, service, severity)
            
            metadata = {
                "service": service,
                "host": host,
                "environment": environment,
                "event_id": str(uuid.uuid4())[:8],
                "correlation_id": str(uuid.uuid4())[:12]
            }
            
            # Add type-specific metadata
            if event_type == "deployment":
                metadata.update({
                    "version": f"v{random.randint(1,5)}.{random.randint(0,20)}.{random.randint(0,10)}",
                    "deployment_id": f"dep_{uuid.uuid4().hex[:8]}"
                })
            elif event_type == "scaling":
                metadata["instance_count"] = random.randint(2, 10)
            elif event_type == "alert":
                metadata["alert_rule"] = random.choice(["high_cpu", "high_memory", "error_rate"])
            
            event = EventRecord(
                timestamp=timestamp,
                event_type=event_type,
                severity=severity,
                source=source,
                message=message,
                metadata=metadata
            )
            
            events.append(event)
            timestamp += timedelta(seconds=random.uniform(10, 300))
        
        return events
    
    def _choose_severity(self, event_type: str) -> EventSeverity:
        """Choose appropriate severity for event type."""
        severity_weights = {
            "deployment": [0.1, 0.8, 0.1, 0.0, 0.0],  # mostly info
            "scaling": [0.0, 0.9, 0.1, 0.0, 0.0],
            "alert": [0.0, 0.2, 0.5, 0.3, 0.0],       # mostly warn/error
            "incident": [0.0, 0.0, 0.3, 0.5, 0.2],    # mostly error/critical
            "maintenance": [0.0, 0.9, 0.1, 0.0, 0.0],
            "security": [0.0, 0.3, 0.4, 0.2, 0.1],
            "backup": [0.1, 0.8, 0.1, 0.0, 0.0],
            "configuration": [0.1, 0.7, 0.2, 0.0, 0.0],
            "network": [0.0, 0.4, 0.4, 0.2, 0.0],
            "performance": [0.0, 0.3, 0.5, 0.2, 0.0]
        }
        
        severities = [EventSeverity.DEBUG, EventSeverity.INFO, EventSeverity.WARN, 
                     EventSeverity.ERROR, EventSeverity.CRITICAL]
        weights = severity_weights.get(event_type, [0.2, 0.6, 0.2, 0.0, 0.0])
        
        return random.choices(severities, weights=weights)[0]
    
    def _generate_message(self, event_type: str, service: str, severity: EventSeverity) -> str:
        """Generate appropriate message for event."""
        templates = {
            "deployment": [
                f"Service {service} version {{version}} deployed successfully",
                f"Deployment of {service} completed in {{duration}}",
                f"Rolling update of {service} started"
            ],
            "scaling": [
                f"Auto-scaling {service} from {{old_count}} to {{new_count}} instances",
                f"Scaling event triggered for {service}",
                f"Instance count adjusted for {service}"
            ],
            "alert": [
                f"Alert triggered: High CPU usage on {service}",
                f"Memory threshold exceeded for {service}",
                f"Error rate spike detected in {service}"
            ],
            "incident": [
                f"Service {service} experiencing degraded performance",
                f"Incident detected: {service} unavailable",
                f"Critical issue affecting {service}"
            ]
        }
        
        default_templates = [
            f"Event occurred in {service}",
            f"Operational event for {service}",
            f"{event_type} event triggered"
        ]
        
        message_templates = templates.get(event_type, default_templates)
        message = random.choice(message_templates)
        
        # Fill in template variables
        if "{version}" in message:
            version = f"v{random.randint(1,5)}.{random.randint(0,20)}.{random.randint(0,10)}"
            message = message.replace("{version}", version)
        if "{duration}" in message:
            message = message.replace("{duration}", f"{random.randint(30, 300)}s")
        if "{old_count}" in message and "{new_count}" in message:
            old_count = random.randint(2, 8)
            new_count = random.randint(2, 12)
            message = message.replace("{old_count}", str(old_count)).replace("{new_count}", str(new_count))
        
        return message