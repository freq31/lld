

import threading
from inventory_management.product import Product
from inventory_management.warehouse import WareHouse


class InventoryManager:
    warehouses: dict[str, WareHouse]
    _warehouse_lock: dict[str, threading.RLock]

    def add(self, product: Product, quantity: int, warehouse_number: str):
        if warehouse_number not in self.warehouses:
            raise ValueError(f"Given warehouse- {warehouse_number} not found")
        
        _lock = self._warehouse_lock[warehouse_number]
        with _lock:
            warehouse = self.warehouses[warehouse_number]
            warehouse.add(product, quantity)

    def remove(self, product: Product, quantity: int, warehouse_number: str):
        if warehouse_number not in self.warehouses:
            raise ValueError(f"Given warehouse- {warehouse_number} not found")
        
        _lock = self._warehouse_lock[warehouse_number]
        with _lock:
            warehouse = self.warehouses[warehouse_number]
            warehouse.remove(product, quantity)

    def transfer(self, product: Product, quantity: int, warehouse_from_number: str, warehouse_to_number: str) -> bool:
        if warehouse_from_number == warehouse_to_number:
            return False
        
        if warehouse_from_number not in self.warehouses or warehouse_to_number not in self.warehouses:
            return False

        warehouse_first = warehouse_from_number if warehouse_from_number < warehouse_to_number else warehouse_to_number
        warehouse_second = warehouse_from_number if warehouse_from_number > warehouse_to_number else warehouse_to_number

        lock_first= self._warehouse_lock[warehouse_first]
        lock_second= self._warehouse_lock[warehouse_second]

        with lock_first:
            with lock_second:
                if warehouse_first == warehouse_from_number:
                    try:
                        self.warehouses[warehouse_first].remove(product, quantity)
                    except Exception as e:
                        print(f"Couldn't remove from - {warehouse_first}")
                        return False
                    try:
                        self.warehouses[warehouse_second].add(product, quantity)
                        return True
                    except Exception as e:
                        print(f"Couldn't remove to - {warehouse_second}")
                        self.warehouses[warehouse_first].add(product, quantity)
                        return False
                    
                else:
                    try:
                        self.warehouses[warehouse_second].remove(product, quantity)
                    except Exception as e:
                        print(f"Couldn't remove from - {warehouse_second}")
                        return False
                    try:
                        self.warehouses[warehouse_first].add(product, quantity)
                        return True
                    except Exception as e:
                        print(f"Couldn't remove to - {warehouse_first}")
                        self.warehouses[warehouse_second].add(product, quantity)
                        return False

    def update_alert_config(self, product: Product, quantity: int, warehouse_number: str, new_threshold: int):
        if warehouse_number not in self.warehouses:
            raise ValueError(f"Given warehouse- {warehouse_number} not found")
        
        _lock = self._warehouse_lock[warehouse_number]
        with _lock:
            warehouse = self.warehouses[warehouse_number]
            warehouse.remove(product, quantity)



    
                


