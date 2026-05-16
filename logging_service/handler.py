from abc import ABC, abstractmethod

from logging_service.formatter import LogFormatter
from logging_service.log_record import LogRecord
from logging_service.loglevel import LogLevel

class LogHandler(ABC):
    formatter: LogFormatter
    logLevel: LogLevel

    def __init__(self, formatter: LogFormatter, logLevel: LogLevel):    
        self.formatter = formatter
        self.logLevel = logLevel
    
    @abstractmethod
    def emit(self, log_record: LogRecord) -> None:
        pass    