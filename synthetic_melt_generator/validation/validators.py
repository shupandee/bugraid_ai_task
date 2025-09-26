"""
Data validator for synthetic MELT data.
"""

import json
import jsonschema
from pathlib import Path
from typing import Dict, Any, List


class DataValidator:
    """Validator for synthetic MELT data."""
    
    def __init__(self):
        self.schemas = {}
    
    def validate_directory(self, data_dir: str) -> Dict[str, Any]:
        """Validate all data files in a directory."""
        data_path = Path(data_dir)
        
        report = {
            "summary": {
                "total_files": 0,
                "valid_files": 0,
                "invalid_files": 0,
                "total_records": 0
            },
            "files": {}
        }
        
        # Load schemas from metadata if available
        metadata_file = data_path / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                metadata = json.load(f)
                self.schemas = metadata.get("schemas", {})
        
        # Validate each data file
        for file_path in data_path.glob("*.jsonl"):
            file_report = self._validate_file(file_path)
            report["files"][file_path.name] = file_report
            
            report["summary"]["total_files"] += 1
            if file_report["valid"]:
                report["summary"]["valid_files"] += 1
            else:
                report["summary"]["invalid_files"] += 1
            
            report["summary"]["total_records"] += file_report["record_count"]
        
        return report
    
    def _validate_file(self, file_path: Path) -> Dict[str, Any]:
        """Validate a single JSONL file."""
        file_report = {
            "valid": True,
            "record_count": 0,
            "errors": []
        }
        
        # Determine data type from filename
        data_type = file_path.stem  # e.g., "metrics" from "metrics.jsonl"
        schema = self.schemas.get(data_type)
        
        try:
            with open(file_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    if line.strip():
                        try:
                            record = json.loads(line)
                            file_report["record_count"] += 1
                            
                            # Validate against schema if available
                            if schema:
                                try:
                                    jsonschema.validate(record, schema)
                                except jsonschema.ValidationError as e:
                                    file_report["valid"] = False
                                    file_report["errors"].append({
                                        "line": line_num,
                                        "error": str(e)
                                    })
                        
                        except json.JSONDecodeError as e:
                            file_report["valid"] = False
                            file_report["errors"].append({
                                "line": line_num,
                                "error": f"Invalid JSON: {str(e)}"
                            })
        
        except Exception as e:
            file_report["valid"] = False
            file_report["errors"].append({
                "file": str(file_path),
                "error": str(e)
            })
        
        return file_report
