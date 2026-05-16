import threading
from inventory_management.alert_config import AlertConfig
from inventory_management.product import Product


class WareHouse:
    warehouse_number: str
    product_map: dict[Product, int]
    alert_config: dict[str, AlertConfig]
    _product_lock: dict[str, threading.RLock]
    
    def add(self, product: Product, quantity: int):
        if product not in self.product_map:
            self.product_map[product]= 0

        _lock = self._product_lock[product.Id]
        with _lock:
            self.product_map[product]+= quantity
        

    def remove(self, product: Product, quantity: int):
        if product not in self.product_map:
            raise ValueError("Product not found")

        _lock = self._product_lock[product.Id]

        with _lock:
            if self.product_map[product] - quantity < 0:
                raise ValueError("Invalid Operation- Product inventory is 0, can't remove further")

            self.product_map[product]-= quantity
            self.check_for_alerts(product, self.product_map[product], self.product_map[product]+quantity ,self.alert_config[product.Id])

    def check_for_alerts(self, product: Product, current_quantity: int, prev_quantity: int, alert_config: AlertConfig):
        if prev_quantity>= alert_config.threshold and current_quantity < alert_config.threshold:
            message = f"Alert!! Quantity for productId- {product.Id} is below the threshold -{alert_config.threshold}"
            alert_config.listener.send_alert(message)

    def update_threshold(self, product: Product, new_threshold: int):
        if product not in self.product_map:
            raise ValueError("Product not found")

        _lock = self._product_lock[product.Id]

        with _lock:
            alert_config= self.alert_config[product.Id]
            old_threshold = alert_config.threshold
            alert_config.updateThreshold(new_threshold)
            if self.product_map[product] >= old_threshold:
                self.check_for_alerts(product, self.product_map[product], old_threshold, new_threshold)
            