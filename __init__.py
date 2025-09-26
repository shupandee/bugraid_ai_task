"""
Synthetic MELT Data Generator

A comprehensive synthetic data generator for MELT (Metrics, Events, Logs, Traces) data
designed for testing anomaly detection and Root Cause Analysis (RCA) systems.
"""

__version__ = "1.0.0"
__author__ = "BugRaid AI Assessment"

from .core.generator import MeltGenerator
from .core.streaming import StreamingGenerator
from .generators.metrics import MetricsGenerator
from .generators.events import EventsGenerator
from .generators.logs import LogsGenerator
from .generators.traces import TracesGenerator

__all__ = [
    "MeltGenerator",
    "StreamingGenerator", 
    "MetricsGenerator",
    "EventsGenerator",
    "LogsGenerator",
    "TracesGenerator",
]
