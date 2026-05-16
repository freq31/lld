import threading
from logging_service.formatter import LogFormatter
from logging_service.async_handler import AsyncHandler
from logging_service.log_record import LogRecord
from logging_service.loglevel import LogLevel


class AsyncConsoleHandler(AsyncHandler):
    """
    Asynchronous console handler that writes log records to stdout.
    
    Log records are queued and written by a background worker thread,
    allowing the emit() method to return immediately.
    """
    _lock: threading.RLock

    def __init__(self, formatter: LogFormatter, logLevel: LogLevel, queue_size: int = 1000):
        super().__init__(formatter, logLevel, queue_size)
        self._lock = threading.RLock()

    def handle(self, log_record: LogRecord):
        """Write formatted log record to console."""
        formatted_message = self.formatter.format(log_record)
        
        with self._lock:
            try:
                print(formatted_message)
            except Exception as e:
                print(f"Error writing to console: {e}")
