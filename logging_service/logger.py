from datetime import datetime
import threading
from typing import List
from logging_service.handler import LogHandler
from logging_service.log_record import LogRecord
from logging_service.loglevel import LogLevel
from logging_service.context import LogContext


class Logger:
    handlers: List[LogHandler]

    def __init__(self, handlers: List[LogHandler]):
        self.handlers = handlers

    def log(self, log_level: LogLevel, message: str):
        """Log a message with the given log level, including trace_id."""
        # Get or generate trace_id from context
        trace_id = LogContext.get('trace_id') or LogContext.generate_trace_id()
        
        log_record = LogRecord(
            timestamp=datetime.now(),
            log_level=log_level,
            message=message,
            thread_id=threading.current_thread().name,
            trace_id=trace_id
        )
        
        for handler in self.handlers:
            handler.emit(log_record)

    def info(self, message: str):
        self.log(LogLevel.INFO, message)

    def debug(self, message: str):
        self.log(LogLevel.DEBUG, message)

    def error(self, message: str):
        self.log(LogLevel.ERROR, message)

    def warning(self, message: str):
        self.log(LogLevel.WARNING, message)

    def critical(self, message: str):
        self.log(LogLevel.CRITICAL, message)