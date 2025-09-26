"""
Generator for synthetic logs data.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
from faker import Faker

from ..core.models import GenerationConfig, LogRecord, LogLevel

fake = Faker()


class LogsGenerator:
    """Generator for application logs."""
    
    def __init__(self, config: GenerationConfig):
        self.config = config
        self.message_templates = {
            LogLevel.DEBUG: [
                "Debug information: processing request {request_id}",
                "Database query executed: {query}",
                "Cache hit for key {key}",
                "Processing user action: {action}"
            ],
            LogLevel.INFO: [
                "User {user_id} logged in successfully",
                "Request processed successfully",
                "Service started successfully",
                "Configuration loaded",
                "Health check passed"
            ],
            LogLevel.WARN: [
                "Slow query detected: {query} took {duration}ms",
                "High memory usage: {usage}%",
                "Deprecated API endpoint used: {endpoint}",
                "Connection pool nearly exhausted"
            ],
            LogLevel.ERROR: [
                "Database connection failed",
                "Failed to process request: {error}",
                "Authentication failed for user {user_id}",
                "External service unavailable",
                "Validation error: {field} is required"
            ],
            LogLevel.CRITICAL: [
                "Service is shutting down due to critical error",
                "Database connection pool exhausted",
                "Out of memory error",
                "Security breach detected"
            ]
        }
    
    def generate_batch(self, timestamp: datetime, count: int) -> List[LogRecord]:
        """Generate a batch of log records."""
        logs = []
        
        for _ in range(count):
            service = random.choice(self.config.services)
            host = random.choice(self.config.hosts)
            environment = random.choice(self.config.environments)
            
            # Choose log level based on error rate and debug ratio
            level = self._choose_log_level()
            
            # Generate message
            message = self._generate_message(level)
            
            # Sometimes include trace info
            trace_id = None
            span_id = None
            if random.random() < 0.3:  # 30% of logs have trace info
                trace_id = uuid.uuid4().hex[:16]
                span_id = uuid.uuid4().hex[:8]
            
            metadata = {
                "service": service,
                "host": host,
                "environment": environment,
                "version": f"v{random.randint(1,3)}.{random.randint(0,10)}.{random.randint(0,5)}",
                "thread_id": random.randint(1, 100),
                "process_id": random.randint(1000, 9999)
            }
            
            log = LogRecord(
                timestamp=timestamp,
                level=level,
                service=service,
                message=message,
                trace_id=trace_id,
                span_id=span_id,
                metadata=metadata
            )
            
            logs.append(log)
            timestamp += timedelta(milliseconds=random.randint(100, 1000))
        
        return logs
    
    def _choose_log_level(self) -> LogLevel:
        """Choose log level based on configuration."""
        # Weight distribution: DEBUG, INFO, WARN, ERROR, CRITICAL
        weights = [
            self.config.debug_log_ratio,          # DEBUG
            0.7 - self.config.debug_log_ratio,    # INFO (majority)
            0.15,                                 # WARN
            self.config.error_rate,               # ERROR
            self.config.error_rate / 10           # CRITICAL (rare)
        ]
        
        levels = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARN, LogLevel.ERROR, LogLevel.CRITICAL]
        return random.choices(levels, weights=weights)[0]
    
    def _generate_message(self, level: LogLevel) -> str:
        """Generate appropriate message for log level."""
        templates = self.message_templates[level]
        message = random.choice(templates)
        
        # Fill in template variables
        replacements = {
            "{request_id}": f"req_{uuid.uuid4().hex[:8]}",
            "{user_id}": f"user_{random.randint(1000, 9999)}",
            "{query}": random.choice(["SELECT * FROM users", "UPDATE orders SET status", "INSERT INTO logs"]),
            "{key}": f"cache_key_{random.randint(1, 1000)}",
            "{action}": random.choice(["login", "logout", "purchase", "search"]),
            "{error}": random.choice(["timeout", "validation failed", "service unavailable"]),
            "{duration}": str(random.randint(100, 5000)),
            "{usage}": str(random.randint(80, 95)),
            "{endpoint}": random.choice(["/api/v1/users", "/api/v1/orders", "/legacy/stats"]),
            "{field}": random.choice(["email", "password", "user_id", "order_id"])
        }
        
        for placeholder, value in replacements.items():
            message = message.replace(placeholder, value)
        
        return message