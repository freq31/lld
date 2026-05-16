import threading
from typing import Any, Dict, Optional
import uuid


class LogContext:
    """
    Thread-safe context manager for storing and accessing contextual logging data
    like trace_id, request_id, user_id, etc. using thread-local storage.
    """
    _context = threading.local()

    @classmethod
    def set(self, key: str, value: Any) -> None:
        """Store a value in the current thread's context."""
        if not hasattr(self._context, 'data'):
            self._context.data = {}
        self._context.data[key] = value

    @classmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from the current thread's context."""
        if not hasattr(self._context, 'data'):
            return default
        return self._context.data.get(key, default)

    @classmethod
    def get_all(self) -> Dict[str, Any]:
        """Get all context data for the current thread."""
        if not hasattr(self._context, 'data'):
            return {}
        return self._context.data.copy()

    @classmethod
    def remove(self, key: str) -> None:
        """Remove a specific key from context."""
        if hasattr(self._context, 'data') and key in self._context.data:
            del self._context.data[key]

    @classmethod
    def clear(self) -> None:
        """Clear all context data for the current thread."""
        if hasattr(self._context, 'data'):
            self._context.data.clear()

    @classmethod
    def generate_trace_id(self) -> str:
        """Generate and set a new trace_id if not already present."""
        existing_trace_id = self.get('trace_id')
        if existing_trace_id:
            return existing_trace_id
        
        trace_id = str(uuid.uuid4())
        self.set('trace_id', trace_id)
        return trace_id

    @classmethod
    def __enter__(self):
        """Context manager entry - can be used with 'with' statement."""
        return self

    @classmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - clears context."""
        self.clear()
        return False
