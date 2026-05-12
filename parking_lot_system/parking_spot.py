from parking_lot_system.vehicle import Vehicle, VehicleType

class ParkingSpot:
    def __init__(self, spot_id: str, vehicle_type: VehicleType):
        self.spot_id = spot_id
        self.vehicle_type = vehicle_type
        self.is_occupied = False

    def can_fit_vehicle(self, vehicle: Vehicle) -> bool:
        return vehicle.vehicle_type == self.vehicle_type
    
    def can_park_vehicle(self, vehicle: Vehicle) -> bool:
        return self.can_fit_vehicle(vehicle) and not self.is_occupied

    def park_vehicle(self, vehicle: Vehicle) -> bool:
        if self.can_park_vehicle(vehicle):
            self.is_occupied = True
            return True
        return False

    def remove_vehicle(self) -> None:
        self.is_occupied = False

