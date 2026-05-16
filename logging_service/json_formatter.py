import json
from logging_service.formatter import LogFormatter
from logging_service.log_record import LogRecord


class JSONLogFormatter(LogFormatter):
    def format(self, log_record: LogRecord) -> str:
        log_dict= {
            "timestamp": log_record.timestamp,
            "log_level": log_record.log_level,
            "message": log_record.message,
            "thread_id": log_record.thread_id,
            "trace_id": log_record.trace_id
        }
        return json.dumps(log_dict)