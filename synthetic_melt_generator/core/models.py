from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO" 
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class EventSeverity(Enum):
    debug = "debug"
    info = "info"
    warn = "warn" 
    error = "error"
    critical = "critical"

class TraceStatus(Enum):
    ok = "ok"
    error = "error"
    timeout = "timeout"

@dataclass
class GenerationConfig:
    seed: int = 42
    duration_hours: float = 1.0
    services: List[str] = field(default_factory=lambda: ["api", "web", "database"])
    hosts: List[str] = field(default_factory=lambda: ["web-01", "web-02", "db-01"])
    environments: List[str] = field(default_factory=lambda: ["production"])
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
    cpu_spike_probability: float = 0.05
    error_burst_probability: float = 0.02
    latency_spike_probability: float = 0.03
    service_outage_probability: float = 0.01

# Metric-related classes
@dataclass  
class Metric:
    timestamp: str
    metric_name: str
    value: float
    labels: Dict[str, str]
    anomaly: bool = False

@dataclass
class MetricPoint:
    timestamp: str
    metric_name: str
    value: float
    labels: Dict[str, str]
    anomaly: bool = False

# Event-related classes
@dataclass
class Event:
    timestamp: str
    event_type: str
    severity: EventSeverity
    source: str
    message: str
    metadata: Dict[str, Any]

@dataclass
class EventRecord:
    timestamp: str
    event_type: str
    severity: EventSeverity
    source: str
    message: str
    metadata: Dict[str, Any]

# Log-related classes
@dataclass
class Log:
    timestamp: str
    level: LogLevel
    service: str
    message: str
    metadata: Dict[str, Any]
    trace_id: Optional[str] = None
    span_id: Optional[str] = None

@dataclass
class LogRecord:
    timestamp: str
    level: LogLevel
    service: str
    message: str
    metadata: Dict[str, Any]
    trace_id: Optional[str] = None
    span_id: Optional[str] = None

# Trace-related classes
@dataclass
class Trace:
    trace_id: str
    span_id: str
    operation_name: str
    start_time: str
    duration: int
    service: str
    tags: Dict[str, str]
    status: str = "ok"
    parent_span_id: Optional[str] = None

@dataclass
class TraceSpan:
    trace_id: str
    span_id: str
    operation_name: str
    start_time: str
    duration: int
    service: str
    tags: Dict[str, str]
    status: str = "ok"
    parent_span_id: Optional[str] = None

class MeltData:
    def __init__(self):
        self.metrics: List[Metric] = []
        self.events: List[Event] = []
        self.logs: List[Log] = []
        self.traces: List[Trace] = []
    
    def total_records(self) -> int:
        return len(self.metrics) + len(self.events) + len(self.logs) + len(self.traces)