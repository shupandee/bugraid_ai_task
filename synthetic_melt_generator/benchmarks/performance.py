"""
Performance benchmarking for synthetic MELT data generator.
"""

import time
import psutil
from typing import Dict, Any, List
from ..core.generator import MeltGenerator
from ..core.models import GenerationConfig


class PerformanceBenchmark:
    """Performance benchmarking for the MELT generator."""
    
    def __init__(self):
        self.results = {}
    
    def run_benchmarks(self, sizes: List[str], iterations: int = 3) -> Dict[str, Any]:
        """Run performance benchmarks for different data sizes."""
        results = {}
        
        for size in sizes:
            print(f"Benchmarking {size}...")
            size_results = []
            
            for i in range(iterations):
                print(f"  Iteration {i + 1}/{iterations}")
                result = self._benchmark_single_run(size)
                size_results.append(result)
            
            # Calculate averages
            avg_result = self._calculate_averages(size_results)
            results[size] = avg_result
        
        return results
    
    def _benchmark_single_run(self, size: str) -> Dict[str, Any]:
        """Run a single benchmark for a given size."""
        # Setup
        config = GenerationConfig(seed=42, duration_hours=1)
        generator = MeltGenerator(config)
        
        # Monitor initial state
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        start_time = time.time()
        
        # Generate data
        data = generator.generate(size=size, anomalies=None)
        
        # Monitor final state
        end_time = time.time()
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Calculate metrics
        generation_time = end_time - start_time
        memory_usage = final_memory - initial_memory
        total_records = data.total_records()
        records_per_second = total_records / generation_time if generation_time > 0 else 0
        
        return {
            "generation_time": generation_time,
            "memory_usage": memory_usage,
            "total_records": total_records,
            "records_per_second": records_per_second,
            "metrics_count": len(data.metrics),
            "events_count": len(data.events),
            "logs_count": len(data.logs),
            "traces_count": len(data.traces)
        }
    
    def _calculate_averages(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate average results from multiple runs."""
        if not results:
            return {}
        
        avg_result = {}
        for key in results[0].keys():
            values = [r[key] for r in results]
            avg_result[f"avg_{key}"] = sum(values) / len(values)
            avg_result[f"min_{key}"] = min(values)
            avg_result[f"max_{key}"] = max(values)
        
        return avg_result
