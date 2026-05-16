
import threading
from logging_service.formatter import LogFormatter
from logging_service.handler import LogHandler
from logging_service.log_record import LogRecord
from logging_service.loglevel import LogLevel


class ConsoleHandler(LogHandler):
    _lock: threading.RLock

    def __init__(self, formatter: LogFormatter, logLevel: LogLevel):
        super().__init__(formatter, logLevel)
        self._lock = threading.RLock()

    def emit(self, log_record: LogRecord):  
        if log_record.log_level.value < self.logLevel.value:
            return
        
        formatted_message = self.formatter.format(log_record)
        
        with self._lock:
            try:
                print(formatted_message)
            except Exception as e:
                print(f"Error writing to console: {e}")