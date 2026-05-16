from logging_service.loglevel import LogLevel


class LogRecord:
    timestamp: float
    log_level : LogLevel
    message: str
    thread_id: str
    trace_id: str

    def __init__(self, timestamp: float, log_level: LogLevel, message: str, thread_id: str, trace_id: str):
        self.timestamp = timestamp
        self.log_level = log_level
        self.message = message
        self.thread_id = thread_id
        self.trace_id = trace_id
