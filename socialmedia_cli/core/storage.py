"""Storage utilities for socialmedia-cli."""
import json
from pathlib import Path
from typing import List, Dict, Any

def save_jsonl(path: Path, records: List[Dict[str, Any]]) -> None:
    """Save records to a JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        for record in records:
            f.write(json.dumps(record) + '\n')

def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Load records from a JSONL file."""
    if not path.exists():
        return []
    
    records = []
    with open(path) as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records 