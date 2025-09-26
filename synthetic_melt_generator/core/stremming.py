"""
Streaming generator for large MELT datasets.
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Generator

from .models import GenerationConfig, AnomalyConfig, MeltData
from .generator import MeltGenerator


class StreamingGenerator:
    """Memory-efficient streaming generator for large datasets."""
    
    def __init__(self, config: GenerationConfig, anomaly_config: Optional[AnomalyConfig] = None):
        self.config = config
        self.anomaly_config = anomaly_config
        self.chunk_size_mb = 100  # Process in 100MB chunks
        
    def generate_streaming(self, total_size: str, anomalies: Optional[List[str]] = None, 
                         output_dir: str = "./output"):
        """Generate large dataset in streaming fashion."""
        print(f"Starting streaming generation of {total_size} data...")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Parse total size
        total_bytes = self._parse_size(total_size)
        chunk_size_bytes = self._parse_size(f"{self.chunk_size_mb}MB")
        
        # Calculate number of chunks needed
        num_chunks = max(1, total_bytes // chunk_size_bytes)
        
        # Initialize file handles
        file_handles = self._initialize_files(output_path)
        
        # Generate data in chunks
        total_records = 0
        start_time = time.time()
        
        try:
            for chunk_num in range(num_chunks):
                print(f"Processing chunk {chunk_num + 1}/{num_chunks}...")
                
                # Generate chunk
                chunk_generator = MeltGenerator(self.config, self.anomaly_config)
                chunk_data = chunk_generator.generate(
                    size=f"{self.chunk_size_mb}MB",
                    anomalies=anomalies
                )
                
                # Stream write chunk data
                self._write_chunk(chunk_data, file_handles)
                total_records += chunk_data.total_records()
                
                # Progress update
                progress = (chunk_num + 1) / num_chunks * 100
                print(f"Progress: {progress:.1f}% ({total_records:,} records)")
        
        finally:
            # Close file handles
            for handle in file_handles.values():
                handle.close()
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        # Write metadata
        self._write_streaming_metadata(output_path, total_records, generation_time, anomalies)
        
        print(f"Streaming generation complete!")
        print(f"Total records: {total_records:,}")
        print(f"Generation time: {generation_time:.2f}s")
        print(f"Rate: {total_records / generation_time:.0f} records/sec")
    
    def _initialize_files(self, output_path: Path) -> dict:
        """Initialize output files for streaming."""
        file_handles = {}
        
        # Open all JSONL files for writing
        for data_type in ["metrics", "events", "logs", "traces"]:
            file_path = output_path / f"{data_type}.jsonl"
            file_handles[data_type] = open(file_path, 'w')
        
        return file_handles
    
    def _write_chunk(self, chunk_data: MeltData, file_handles: dict):
        """Write chunk data to files."""
        # Write metrics
        for metric in chunk_data.metrics:
            json.dump(metric.model_dump(mode='json', serialize_as_any=True), 
                     file_handles["metrics"], default=str)
            file_handles["metrics"].write('\n')
        
        # Write events
        for event in chunk_data.events:
            json.dump(event.model_dump(mode='json', serialize_as_any=True), 
                     file_handles["events"], default=str)
            file_handles["events"].write('\n')
        
        # Write logs
        for log in chunk_data.logs:
            json.dump(log.model_dump(mode='json', serialize_as_any=True), 
                     file_handles["logs"], default=str)
            file_handles["logs"].write('\n')
        
        # Write traces
        for trace in chunk_data.traces:
            json.dump(trace.model_dump(mode='json', serialize_as_any=True), 
                     file_handles["traces"], default=str)
            file_handles["traces"].write('\n')
        
        # Flush buffers periodically
        for handle in file_handles.values():
            handle.flush()
    
    def _write_streaming_metadata(self, output_path: Path, total_records: int, 
                                generation_time: float, anomalies: Optional[List[str]]):
        """Write metadata for streaming generation."""
        
        # Calculate file sizes
        file_sizes = {}
        total_size_mb = 0
        
        for data_type in ["metrics", "events", "logs", "traces"]:
            file_path = output_path / f"{data_type}.jsonl"
            if file_path.exists():
                size_bytes = file_path.stat().st_size
                size_mb = size_bytes / (1024 * 1024)
                file_sizes[data_type] = {
                    "size_bytes": size_bytes,
                    "size_mb": round(size_mb, 2)
                }
                total_size_mb += size_mb
        
        # Write metadata
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "generator_version": "1.0.0",
            "generation_mode": "streaming",
            "data_types": list(file_sizes.keys()),
            "total_records": total_records,
            "total_size_mb": round(total_size_mb, 2),
            "generation_time_seconds": round(generation_time, 2),
            "records_per_second": round(total_records / generation_time, 0),
            "file_sizes": file_sizes,
            "anomalies_injected": anomalies or [],
            "generation_config": self.config.model_dump(),
            "anomaly_config": self.anomaly_config.model_dump() if self.anomaly_config else None
        }
        
        metadata_file = output_path / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        # Write statistics
        stats = {
            "total_records": total_records,
            "metrics_count": self._count_lines(output_path / "metrics.jsonl"),
            "events_count": self._count_lines(output_path / "events.jsonl"),
            "logs_count": self._count_lines(output_path / "logs.jsonl"),
            "traces_count": self._count_lines(output_path / "traces.jsonl"),
            "generation_time_seconds": generation_time,
            "output_size_mb": total_size_mb
        }
        
        stats_file = output_path / "statistics.json"
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2, default=str)
    
    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file efficiently."""
        if not file_path.exists():
            return 0
        
        try:
            with open(file_path, 'r') as f:
                return sum(1 for line in f if line.strip())
        except Exception:
            return 0
    
    def _parse_size(self, size: str) -> int:
        """Parse size string to bytes."""
        size = size.upper()
        multipliers = {
            'B': 1,
            'KB': 1024,
            'MB': 1024**2,
            'GB': 1024**3,
            'TB': 1024**4
        }
        
        for suffix, multiplier in multipliers.items():
            if size.endswith(suffix):
                number = float(size[:-len(suffix)])
                return int(number * multiplier)
        
        # Default to bytes if no suffix
        return int(size)