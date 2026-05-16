from logging_service.formatter import LogFormatter
from logging_service.log_record import LogRecord


class PlainTextLogFormatter(LogFormatter):
    def format(self, log_record: LogRecord) -> str:
        return f"{log_record.trace_id} - {log_record.timestamp} - {log_record.log_level} - {log_record.message} - (Thread: {log_record.thread_id})"
