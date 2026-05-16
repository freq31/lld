
from abc import ABC, abstractmethod

from logging_service.log_record import LogRecord

class LogFormatter(ABC):
    @abstractmethod
    def format(self, log_record: LogRecord) -> str:
        pass
