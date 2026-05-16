from abc import ABC, abstractmethod

class AlertListener(ABC):
    @abstractmethod
    def send_alert(self, message: str):
        pass