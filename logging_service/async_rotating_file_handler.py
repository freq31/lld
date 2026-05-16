import os
import threading
from logging_service.formatter import LogFormatter
from logging_service.async_handler import AsyncHandler
from logging_service.log_record import LogRecord
from logging_service.loglevel import LogLevel


class AsyncRotatingFileHandler(AsyncHandler):
    """
    Asynchronous rotating file handler that writes log records to files with rotation.
    
    Features:
    - Log records are queued and written by a background worker thread
    - Automatically rotates files when they exceed max_file_size
    - Keeps only the last backup_count backup files
    - emit() returns immediately without blocking on I/O
    """
    file_path: str
    max_file_size: float
    backup_count: int
    _lock: threading.RLock

    def __init__(self, formatter: LogFormatter, logLevel: LogLevel, file_path: str, 
                 max_file_size: float, backup_count: int = 5, queue_size: int = 1000):
        """
        Initialize async rotating file handler.
        
        Args:
            formatter: LogFormatter instance
            logLevel: Minimum log level to handle
            file_path: Path to the main log file
            max_file_size: Maximum file size in bytes before rotation
            backup_count: Number of backup files to keep (default: 5)
            queue_size: Maximum size of the log queue (0 = unlimited)
        """
        self.file_path = file_path
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self._lock = threading.RLock()
        super().__init__(formatter, logLevel, queue_size)

    def handle(self, log_record: LogRecord):
        """Write formatted log record to file with rotation."""
        formatted_message = self.formatter.format(log_record)
        
        with self._lock:
            try:
                if self._should_rotate():
                    self._rotate_file()
                    self._create_new_file()
                
                with open(self.file_path, 'a') as log_file:
                    log_file.write(formatted_message + '\n')
            except Exception as e:
                print(f"Error writing to log file: {e}")

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
