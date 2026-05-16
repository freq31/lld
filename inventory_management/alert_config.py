from inventory_management.alert_listener import AlertListener

class AlertConfig:
    threshold: int
    listener: AlertListener

    def updateThreshold(self, new_threshold: int):
        self.threshold = new_threshold