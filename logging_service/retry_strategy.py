import time
from abc import ABC, abstractmethod
from enum import Enum


class RetryStrategy(Enum):
    """Enumeration of retry strategies."""
    NO_RETRY = "no_retry"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"


class FallbackStrategy(ABC):
    """Abstract base class for fallback strategies."""
    
    @abstractmethod
    def should_retry(self, attempt: int, exception: Exception) -> bool:
        """Determine if retry should happen."""
        pass
    
    @abstractmethod
    def get_delay(self, attempt: int) -> float:
        """Get delay before next retry in seconds."""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get the name of the strategy."""
        pass


class NoRetryStrategy(FallbackStrategy):
    """No retry - fail immediately."""
    
    def should_retry(self, attempt: int, exception: Exception) -> bool:
        return False
    
    def get_delay(self, attempt: int) -> float:
        return 0.0
    
    def get_strategy_name(self) -> str:
        return "NoRetry"


class FixedDelayStrategy(FallbackStrategy):
    """Retry with fixed delay between attempts."""
    
    def __init__(self, max_retries: int = 3, delay: float = 1.0):
        """
        Args:
            max_retries: Maximum number of retry attempts
            delay: Fixed delay in seconds between retries
        """
        self.max_retries = max_retries
        self.delay = delay
    
    def should_retry(self, attempt: int, exception: Exception) -> bool:
        return attempt < self.max_retries
    
    def get_delay(self, attempt: int) -> float:
        return self.delay
    
    def get_strategy_name(self) -> str:
        return f"FixedDelay(max_retries={self.max_retries}, delay={self.delay}s)"


class LinearBackoffStrategy(FallbackStrategy):
    """Retry with linearly increasing delay."""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 0.5):
        """
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay in seconds
        
        Example: With base_delay=0.5:
            Attempt 1: wait 0.5s
            Attempt 2: wait 1.0s
            Attempt 3: wait 1.5s
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    def should_retry(self, attempt: int, exception: Exception) -> bool:
        return attempt < self.max_retries
    
    def get_delay(self, attempt: int) -> float:
        # Delay = base_delay * (attempt + 1)
        return self.base_delay * (attempt + 1)
    
    def get_strategy_name(self) -> str:
        return f"LinearBackoff(max_retries={self.max_retries}, base_delay={self.base_delay}s)"


class ExponentialBackoffStrategy(FallbackStrategy):
    """Retry with exponentially increasing delay."""
    
    def __init__(self, max_retries: int = 5, base_delay: float = 0.1, max_delay: float = 30.0):
        """
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay in seconds
            max_delay: Maximum delay cap in seconds
        
        Example: With base_delay=0.1, max_delay=30:
            Attempt 1: wait 0.1s (0.1 * 2^0)
            Attempt 2: wait 0.2s (0.1 * 2^1)
            Attempt 3: wait 0.4s (0.1 * 2^2)
            Attempt 4: wait 0.8s (0.1 * 2^3)
            Attempt 5: wait 1.6s (0.1 * 2^4)
            ... capped at max_delay=30s
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def should_retry(self, attempt: int, exception: Exception) -> bool:
        return attempt < self.max_retries
    
    def get_delay(self, attempt: int) -> float:
        # Exponential: base_delay * (2 ^ attempt)
        delay = self.base_delay * (2 ** attempt)
        return min(delay, self.max_delay)
    
    def get_strategy_name(self) -> str:
        return f"ExponentialBackoff(max_retries={self.max_retries}, base_delay={self.base_delay}s, max_delay={self.max_delay}s)"


class ExponentialBackoffWithJitterStrategy(FallbackStrategy):
    """Retry with exponential backoff plus random jitter to prevent thundering herd."""
    
    def __init__(self, max_retries: int = 5, base_delay: float = 0.1, max_delay: float = 30.0):
        """
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay in seconds
            max_delay: Maximum delay cap in seconds
        
        Adds random jitter (0-100%) to exponential delay to prevent
        multiple threads retrying at exactly the same time.
        """
        import random
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self._random = random
    
    def should_retry(self, attempt: int, exception: Exception) -> bool:
        return attempt < self.max_retries
    
    def get_delay(self, attempt: int) -> float:
        # Exponential base delay
        delay = self.base_delay * (2 ** attempt)
        delay = min(delay, self.max_delay)
        
        # Add jitter: random value between 0 and delay
        jitter = self._random.uniform(0, delay)
        return jitter
    
    def get_strategy_name(self) -> str:
        return f"ExponentialBackoffWithJitter(max_retries={self.max_retries}, base_delay={self.base_delay}s, max_delay={self.max_delay}s)"


class RetryExecutor:
    """
    Executes operations with retry logic based on a fallback strategy.
    """
    
    def __init__(self, fallback_strategy: FallbackStrategy):
        """
        Args:
            fallback_strategy: Strategy to use for retries
        """
        self.strategy = fallback_strategy
    
    def execute(self, operation, *args, **kwargs):
        """
        Execute operation with retry logic.
        
        Args:
            operation: Callable to execute
            *args: Positional arguments for operation
            **kwargs: Keyword arguments for operation
        
        Returns:
            Result of successful operation
        
        Raises:
            Exception: If all retries fail
        """
        attempt = 0
        last_exception = None
        
        while True:
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if not self.strategy.should_retry(attempt, e):
                    print(f"[{self.strategy.get_strategy_name()}] Max retries exhausted after {attempt} attempts")
                    raise
                
                delay = self.strategy.get_delay(attempt)
                print(f"[{self.strategy.get_strategy_name()}] Attempt {attempt + 1} failed: {type(e).__name__}: {str(e)}")
                print(f"[{self.strategy.get_strategy_name()}] Retrying in {delay:.2f}s...")
                
                time.sleep(delay)
                attempt += 1
