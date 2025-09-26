# MELT Data Schemas

This document describes the data schemas used by the Synthetic MELT Data Generator.

## Overview

The generator produces four types of observability data:
- **Metrics**: Time-series numerical data points
- **Events**: Discrete operational events
- **Logs**: Structured application logs
- **Traces**: Distributed tracing spans

## Metrics Schema

Metrics represent time-series data points with labels and values.

### JSON Schema
```json
{
  "type": "object",
  "properties": {
    "timestamp": {"type": "string", "format": "date-time"},
    "metric_name": {"type": "string"},
    "value": {"type": "number"},
    "labels": {
      "type": "object",
      "properties": {
        "service": {"type": "string"},
        "host": {"type": "string"},
        "environment": {"type": "string"},
        "unit": {"type": "string"}
      },
      "required": ["service", "host", "environment", "unit"]
    },
    "anomaly": {"type": "boolean"}
  },
  "required": ["timestamp", "metric_name", "value", "labels", "anomaly"]
}
```

### Example
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "metric_name": "cpu_usage",
  "value": 45.2,
  "labels": {
    "service": "api",
    "host": "web-01",
    "environment": "production",
    "unit": "percent"
  },
  "anomaly": false
}
```

### Metric Types
- `cpu_usage`: CPU utilization percentage (0-100)
- `memory_usage`: Memory utilization percentage (0-100)
- `disk_usage`: Disk utilization percentage (0-100)
- `network_io`: Network I/O in bytes per second
- `response_time`: Response time in milliseconds
- `error_rate`: Error rate as a ratio (0-1)
- `request_count`: Requests per second
- `database_connections`: Number of active database connections

## Events Schema

Events represent discrete operational occurrences.

### JSON Schema
```json
{
  "type": "object",
  "properties": {
    "timestamp": {"type": "string", "format": "date-time"},
    "event_type": {"type": "string"},
    "severity": {"type": "string", "enum": ["debug", "info", "warn", "error", "critical"]},
    "source": {"type": "string"},
    "message": {"type": "string"},
    "metadata": {
      "type": "object",
      "properties": {
        "service": {"type": "string"},
        "host": {"type": "string"},
        "environment": {"type": "string"},
        "event_id": {"type": "string"},
        "correlation_id": {"type": "string"}
      },
      "required": ["service", "host", "environment", "event_id"]
    }
  },
  "required": ["timestamp", "event_type", "severity", "source", "message", "metadata"]
}
```

### Example
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "event_type": "deployment",
  "severity": "info",
  "source": "ci-cd-pipeline",
  "message": "Service api version v2.1.0 deployed successfully",
  "metadata": {
    "service": "api",
    "host": "web-01",
    "environment": "production",
    "event_id": "evt_12345",
    "correlation_id": "corr_67890",
    "version": "v2.1.0",
    "deployment_id": "dep_abcdef123456"
  }
}
```

### Event Types
- `deployment`: Application deployments
- `scaling`: Auto-scaling events
- `alert`: Monitoring alerts
- `incident`: Service incidents
- `maintenance`: Maintenance activities
- `security`: Security-related events
- `backup`: Backup operations
- `configuration`: Configuration changes
- `network`: Network-related events
- `performance`: Performance issues

## Logs Schema

Logs represent structured application log entries.

### JSON Schema
```json
{
  "type": "object",
  "properties": {
    "timestamp": {"type": "string", "format": "date-time"},
    "level": {"type": "string", "enum": ["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"]},
    "service": {"type": "string"},
    "message": {"type": "string"},
    "trace_id": {"type": ["string", "null"]},
    "span_id": {"type": ["string", "null"]},
    "metadata": {
      "type": "object",
      "properties": {
        "service": {"type": "string"},
        "host": {"type": "string"},
        "environment": {"type": "string"},
        "version": {"type": "string"},
        "thread_id": {"type": "integer"},
        "process_id": {"type": "integer"}
      },
      "required": ["service", "host", "environment"]
    }
  },
  "required": ["timestamp", "level", "service", "message", "metadata"]
}
```

### Example
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "service": "api",
  "message": "User user_1234 logged in successfully",
  "trace_id": "abc123def456789",
  "span_id": "span123",
  "metadata": {
    "service": "api",
    "host": "web-01",
    "environment": "production",
    "version": "v2.1.0",
    "thread_id": 42,
    "process_id": 1234
  }
}
```

### Log Levels
- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages
- `WARN`: Warning messages for potentially harmful situations
- `ERROR`: Error events that might still allow the application to continue
- `CRITICAL`: Very severe error events that might cause the application to abort

## Traces Schema

Traces represent distributed tracing spans.

### JSON Schema
```json
{
  "type": "object",
  "properties": {
    "trace_id": {"type": "string"},
    "span_id": {"type": "string"},
    "parent_span_id": {"type": ["string", "null"]},
    "operation_name": {"type": "string"},
    "start_time": {"type": "string", "format": "date-time"},
    "duration": {"type": "integer", "minimum": 0},
    "service": {"type": "string"},
    "tags": {
      "type": "object",
      "properties": {
        "service.name": {"type": "string"},
        "service.version": {"type": "string"},
        "environment": {"type": "string"},
        "host.name": {"type": "string"}
      },
      "required": ["service.name", "environment"]
    },
    "status": {"type": "string", "enum": ["ok", "error", "timeout"]}
  },
  "required": ["trace_id", "span_id", "operation_name", "start_time", "duration", "service", "tags", "status"]
}
```

### Example
```json
{
  "trace_id": "abc123def456789",
  "span_id": "span123",
  "parent_span_id": "parent456",
  "operation_name": "http_request",
  "start_time": "2024-01-01T12:00:00Z",
  "duration": 150000,
  "service": "api",
  "tags": {
    "service.name": "api",
    "service.version": "v2.1.0",
    "environment": "production",
    "host.name": "web-01",
    "http.method": "GET",
    "http.url": "https://api.example.com/v1/users",
    "http.status_code": "200"
  },
  "status": "ok"
}
```

### Operation Types
- `http_request`: HTTP request handling
- `database_query`: Database operations
- `cache_operation`: Cache interactions
- `message_processing`: Message queue operations
- `file_operation`: File system operations
- `external_api_call`: External service calls

### Span Status
- `ok`: Successful operation
- `error`: Operation failed with an error
- `timeout`: Operation timed out

## Data Relationships

### Correlation
- **Logs and Traces**: Logs include `trace_id` and `span_id` for correlation
- **Events and Metrics**: Events can reference metric anomalies
- **Traces**: Parent-child relationships via `parent_span_id`

### Temporal Alignment
All data types use ISO 8601 timestamps for temporal correlation:
- Metrics: Regular intervals (default 30s)
- Logs: Variable frequency (default 1s intervals)
- Traces: Request-driven timing
- Events: Irregular occurrence

### Anomaly Indicators
- **Metrics**: `anomaly` boolean field
- **Logs**: Higher error/critical log levels during incidents
- **Traces**: `error` or `timeout` status
- **Events**: `incident`, `alert`, or `critical` severity events

## File Formats

### JSONL (JSON Lines)
Default output format with one JSON object per line:
```
{"timestamp": "2024-01-01T12:00:00Z", "metric_name": "cpu_usage", ...}
{"timestamp": "2024-01-01T12:00:30Z", "metric_name": "cpu_usage", ...}
```

### Metadata Files
- `metadata.json`: Generation configuration and schemas
- `statistics.json`: Generation statistics and performance metrics

## Validation

All generated data is validated against these schemas to ensure:
- Required fields are present
- Data types are correct
- Enum values are valid
- Timestamps are properly formatted
- Relationships are maintained

## Extensibility

The schemas support extension through:
- Additional labels in metrics
- Custom metadata in events and logs
- Extra tags in traces
- New metric types and event types
- Custom anomaly indicators
