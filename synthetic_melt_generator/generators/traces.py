"""
Generator for synthetic traces data.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any

from ..core.models import GenerationConfig, TraceSpan, TraceStatus


class TracesGenerator:
    """Generator for distributed tracing spans."""
    
    def __init__(self, config: GenerationConfig):
        self.config = config
        self.operations = {
            "http_request": ["GET /users", "POST /orders", "PUT /users/{id}", "DELETE /orders/{id}"],
            "database_query": ["SELECT users", "UPDATE orders", "INSERT logs", "DELETE sessions"],
            "cache_operation": ["GET user_cache", "SET order_cache", "DEL session_cache"],
            "message_processing": ["process_order", "send_notification", "update_inventory"],
            "file_operation": ["read_config", "write_logs", "backup_data"],
            "external_api_call": ["payment_gateway", "email_service", "analytics_api"]
        }
    
    def generate_batch(self, timestamp: datetime, count: int) -> List[TraceSpan]:
        """Generate a batch of trace spans."""
        traces = []
        
        # Generate traces as trees (parent-child relationships)
        for _ in range(count):
            trace_tree = self._generate_trace_tree(timestamp)
            traces.extend(trace_tree)
        
        return traces
    
    def _generate_trace_tree(self, start_time: datetime) -> List[TraceSpan]:
        """Generate a complete trace tree."""
        trace_id = uuid.uuid4().hex[:16]
        spans = []
        
        # Generate root span
        root_service = random.choice(self.config.services)
        root_operation = random.choice(list(self.operations.keys()))
        root_operation_name = random.choice(self.operations[root_operation])
        
        root_duration = random.randint(50000, 500000)  # 50ms to 500ms in microseconds
        
        root_span = self._create_span(
            trace_id=trace_id,
            span_id=uuid.uuid4().hex[:8],
            parent_span_id=None,
            operation_name=root_operation_name,
            start_time=start_time,
            duration=root_duration,
            service=root_service,
            operation_type=root_operation
        )
        
        spans.append(root_span)
        
        # Generate child spans
        depth = random.randint(1, min(self.config.max_trace_depth, 4))
        self._generate_child_spans(spans, trace_id, root_span, depth, start_time)
        
        return spans
    
    def _generate_child_spans(self, spans: List[TraceSpan], trace_id: str, 
                             parent_span: TraceSpan, remaining_depth: int, 
                             base_time: datetime):
        """Recursively generate child spans."""
        if remaining_depth <= 0:
            return
        
        # Generate 1-3 child spans
        child_count = random.randint(1, 3)
        child_start_offset = 0
        
        for _ in range(child_count):
            # Skip some spans to simulate missing spans
            if random.random() < self.config.missing_span_rate:
                continue
            
            child_service = random.choice(self.config.services)
            child_operation = random.choice(list(self.operations.keys()))
            child_operation_name = random.choice(self.operations[child_operation])
            
            # Child spans start after parent and are shorter
            child_start = base_time + timedelta(microseconds=child_start_offset * 1000)
            child_duration = random.randint(1000, parent_span.duration // 2)
            
            child_span = self._create_span(
                trace_id=trace_id,
                span_id=uuid.uuid4().hex[:8],
                parent_span_id=parent_span.span_id,
                operation_name=child_operation_name,
                start_time=child_start,
                duration=child_duration,
                service=child_service,
                operation_type=child_operation
            )
            
            spans.append(child_span)
            
            # Recursively generate grandchildren
            if remaining_depth > 1 and random.random() < 0.5:
                self._generate_child_spans(spans, trace_id, child_span, 
                                         remaining_depth - 1, child_start)
            
            child_start_offset += child_duration // 1000
    
    def _create_span(self, trace_id: str, span_id: str, parent_span_id: str,
                    operation_name: str, start_time: datetime, duration: int,
                    service: str, operation_type: str) -> TraceSpan:
        """Create a single trace span."""
        
        # Determine status based on error rate
        status = TraceStatus.OK
        if random.random() < self.config.error_rate:
            status = random.choice([TraceStatus.ERROR, TraceStatus.TIMEOUT])
        
        # Create tags based on operation type
        tags = {
            "service.name": service,
            "service.version": f"v{random.randint(1,3)}.{random.randint(0,10)}.0",
            "environment": random.choice(self.config.environments),
            "host.name": random.choice(self.config.hosts)
        }
        
        # Add operation-specific tags
        if operation_type == "http_request":
            tags.update({
                "http.method": operation_name.split()[0],
                "http.url": f"https://api.example.com{operation_name.split()[1]}",
                "http.status_code": "500" if status == TraceStatus.ERROR else "200"
            })
        elif operation_type == "database_query":
            tags.update({
                "db.type": random.choice(["postgresql", "mysql", "redis"]),
                "db.statement": operation_name,
                "db.instance": "primary"
            })
        elif operation_type == "cache_operation":
            tags.update({
                "cache.type": "redis",
                "cache.key": operation_name.split()[1] if len(operation_name.split()) > 1 else "unknown"
            })
        
        return TraceSpan(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            start_time=start_time,
            duration=duration,
            service=service,
            tags=tags,
            status=status
        )