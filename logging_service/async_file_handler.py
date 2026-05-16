import threading
from logging_service.formatter import LogFormatter
from logging_service.async_handler import AsyncHandler
from logging_service.log_record import LogRecord
from logging_service.loglevel import LogLevel


class AsyncFileHandler(AsyncHandler):
    """
    Asynchronous file handler that writes log records to a file.
    
    Log records are queued and written by a background worker thread,
    allowing the emit() method to return immediately without blocking on I/O.
    """
    file_path: str
    _lock: threading.RLock

    def __init__(self, formatter: LogFormatter, logLevel: LogLevel, file_path: str, queue_size: int = 1000):
        """
        Initialize async file handler.
        
        Args:
            formatter: LogFormatter instance
            logLevel: Minimum log level to handle
            file_path: Path to the log file
            queue_size: Maximum size of the log queue (0 = unlimited)
        """
        self.file_path = file_path
        self._lock = threading.RLock()
        super().__init__(formatter, logLevel, queue_size)

    def handle(self, log_record: LogRecord):
        """Write formatted log record to file."""
        formatted_message = self.formatter.format(log_record)
        
        with self._lock:
            try:
                with open(self.file_path, 'a') as log_file:
                    log_file.write(formatted_message + '\n')
            except Exception as e:
                print(f"Error writing to log file: {e}")
