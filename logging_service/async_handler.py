import threading
import queue
from abc import abstractmethod
from logging_service.formatter import LogFormatter
from logging_service.handler import LogHandler
from logging_service.log_record import LogRecord
from logging_service.loglevel import LogLevel


class AsyncHandler(LogHandler):
    """
    Abstract base class for asynchronous log handlers.
    
    Implements a worker thread that processes log records from a queue
    asynchronously, decoupling emit() from the actual I/O operation.
    """
    _queue: queue.Queue
    _worker_thread: threading.Thread
    _stop_event: threading.Event
    _queue_timeout: float = 1.0

    def __init__(self, formatter: LogFormatter, logLevel: LogLevel, queue_size: int = 1000):
        """
        Initialize async handler with a worker thread.
        
        Args:
            formatter: LogFormatter instance
            logLevel: Minimum log level to handle
            queue_size: Maximum size of the log queue (0 = unlimited)
        """
        super().__init__(formatter, logLevel)
        self._queue = queue.Queue(maxsize=queue_size)
        self._stop_event = threading.Event()
        
        # Start worker thread as daemon
        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._worker_thread.start()

    def emit(self, log_record: LogRecord):
        """
        Emit a log record by putting it in the queue.
        This method returns immediately without blocking on I/O.
        """
        if log_record.log_level.value < self.logLevel.value:
            return
        
        try:
            # Non-blocking put with timeout to avoid deadlocks
            self._queue.put_nowait(log_record)
        except queue.Full:
            # If queue is full, try to put with timeout
            try:
                self._queue.put(log_record, timeout=0.1)
            except queue.Full:
                print(f"Warning: Log queue is full, dropping log record")

    def _worker(self):
        """
        Worker thread that continuously processes log records from the queue.
        """
        while not self._stop_event.is_set():
            try:
                # Get log record with timeout to check stop event periodically
                log_record = self._queue.get(timeout=self._queue_timeout)
                if log_record is None:  # Sentinel value to stop worker
                    break
                
                try:
                    self.handle(log_record)
                except Exception as e:
                    print(f"Error handling log record: {e}")
                finally:
                    self._queue.task_done()
            
            except queue.Empty:
                continue
        
        # Process remaining items in queue before exiting
        self._flush_remaining()

    def _flush_remaining(self):
        """Process all remaining log records in the queue."""
        while True:
            try:
                log_record = self._queue.get_nowait()
                if log_record is None:
                    break
                try:
                    self.handle(log_record)
                except Exception as e:
                    print(f"Error handling log record during flush: {e}")
                finally:
                    self._queue.task_done()
            except queue.Empty:
                break

    @abstractmethod
    def handle(self, log_record: LogRecord) -> None:
        """
        Handle a single log record. Subclasses must implement this.
        This method is called by the worker thread.
        """
        pass

    def flush(self):
        """Wait for all queued log records to be processed."""
        self._queue.join()

    def close(self):
        """Stop the worker thread and flush remaining records."""
        self._stop_event.set()
        # Put sentinel value to wake up worker if it's waiting
        try:
            self._queue.put(None, timeout=1.0)
        except queue.Full:
            pass
        
        # Wait for worker thread to finish
        self._worker_thread.join(timeout=5.0)
