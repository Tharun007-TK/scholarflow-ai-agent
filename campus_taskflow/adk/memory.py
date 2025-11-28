from typing import Any, Dict, List, Optional
import json
import os

class MemoryBank:
    """Manages short-term (session) and long-term (vector/file) memory."""
    def __init__(self, memory_dir: str = "memory_store"):
        self.memory_dir = memory_dir
        os.makedirs(memory_dir, exist_ok=True)
        self.session_store: Dict[str, Any] = {}
        self.vector_store: List[Dict[str, Any]] = [] # Simple list-based mock for now

    def store_session(self, key: str, value: Any):
        self.session_store[key] = value

    def retrieve_session(self, key: str) -> Any:
        return self.session_store.get(key)

    def store_long_term(self, collection: str, item: Dict[str, Any]):
        """Stores an item in a JSON-based collection for persistence."""
        file_path = os.path.join(self.memory_dir, f"{collection}.json")
        data = []
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
        
        data.append(item)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def retrieve_long_term(self, collection: str) -> List[Dict[str, Any]]:
        file_path = os.path.join(self.memory_dir, f"{collection}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def clear_session(self):
        self.session_store = {}
