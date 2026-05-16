
import os
import threading
from logging_service.formatter import LogFormatter
from logging_service.handler import LogHandler
from logging_service.log_record import LogRecord
from logging_service.loglevel import LogLevel
from logging_service.retry_strategy import FallbackStrategy, NoRetryStrategy, RetryExecutor


class RotatingFileHandler(LogHandler):
    file_path: str
    max_file_size: float
    backup_count: int
    _lock: threading.RLock
    retry_executor: RetryExecutor

    def __init__(self, formatter: LogFormatter, logLevel: LogLevel, file_path: str, max_file_size: float, 
                 backup_count: int = 5, fallback_strategy: FallbackStrategy = None):
        """
        Initialize rotating file handler with file size-based rotation and retry strategy.
        
        Args:
            formatter: LogFormatter instance
            logLevel: Minimum log level to handle
            file_path: Path to the main log file
            max_file_size: Maximum file size in bytes before rotation
            backup_count: Number of backup files to keep (default: 5)
            fallback_strategy: Strategy for retrying failed writes (default: NoRetryStrategy)
        """
        super().__init__(formatter, logLevel)
        self.file_path = file_path
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self._lock = threading.RLock()
        self.retry_executor = RetryExecutor(fallback_strategy or NoRetryStrategy())

    def emit(self, log_record: LogRecord):  
        if log_record.log_level.value < self.logLevel.value:
            return
        
        formatted_message = self.formatter.format(log_record)
        
        with self._lock:
            try:
                if self._should_rotate():
                    self._rotate_file()
                    self._create_new_file()
                
                self.retry_executor.execute(self._write_to_file, formatted_message)
            except Exception as e:
                print(f"Error writing to log file after retries exhausted: {e}")

    def _write_to_file(self, formatted_message: str):
        """Helper method to write message to file (used by retry executor)."""
        with open(self.file_path, 'a') as log_file:
            log_file.write(formatted_message + '\n')

    def _should_rotate(self) -> bool:
        """Check if current log file exceeds max size."""
        return os.path.exists(self.file_path) and os.path.getsize(self.file_path) >= self.max_file_size
    
    def _rotate_file(self):
        """
        Rotate log files using sequential numbering.
        
        Pattern: app.log (current) → app.log.1 → app.log.2 → ... → app.log.N
        Keeps only the last backup_count files.
        """
        if not os.path.exists(self.file_path):
            return
        
        # Shift existing backups: app.log.2 → app.log.3, app.log.1 → app.log.2, etc.
        for i in range(self.backup_count - 1, 0, -1):
            old_backup = f"{self.file_path}.{i}"
            new_backup = f"{self.file_path}.{i + 1}"
            
            if os.path.exists(old_backup):
                if i == self.backup_count - 1:
                    # Delete the oldest file if it exists
                    os.remove(old_backup)
                else:
                    os.rename(old_backup, new_backup)
        
        # Rename current log to app.log.1
        new_backup = f"{self.file_path}.1"
        os.rename(self.file_path, new_backup)
    
    def _create_new_file(self):
        """Create a fresh log file after rotation."""
        with open(self.file_path, 'w') as new_file:
            pass  # Creates empty file