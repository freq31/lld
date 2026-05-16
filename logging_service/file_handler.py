
import threading
from logging_service.formatter import LogFormatter
from logging_service.handler import LogHandler
from logging_service.log_record import LogRecord
from logging_service.loglevel import LogLevel
from logging_service.retry_strategy import FallbackStrategy, NoRetryStrategy, RetryExecutor


class FileHandler(LogHandler):
    file_path: str
    _lock: threading.RLock
    retry_executor: RetryExecutor

    def __init__(self, formatter: LogFormatter, logLevel: LogLevel, file_path: str, 
                 fallback_strategy: FallbackStrategy = None):
        """
        Initialize file handler with optional retry strategy.
        
        Args:
            formatter: LogFormatter instance
            logLevel: Minimum log level to handle
            file_path: Path to the log file
            fallback_strategy: Strategy for retrying failed writes (default: NoRetryStrategy)
        """
        super().__init__(formatter, logLevel)
        self.file_path = file_path
        self._lock = threading.RLock()
        
        # Use NoRetryStrategy if none provided
        self.retry_executor = RetryExecutor(fallback_strategy or NoRetryStrategy())

    def emit(self, log_record: LogRecord):  
        if log_record.log_level.value < self.logLevel.value:
            return
        
        formatted_message = self.formatter.format(log_record)
        
        with self._lock:
            try:
                self.retry_executor.execute(self._write_to_file, formatted_message)
            except Exception as e:
                print(f"Error writing to log file after retries exhausted: {e}")

    def _write_to_file(self, formatted_message: str):
        """Helper method to write message to file (used by retry executor)."""
        with open(self.file_path, 'a') as log_file:
            log_file.write(formatted_message + '\n')