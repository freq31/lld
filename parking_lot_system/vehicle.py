from enum import Enum

class VehicleType(str, Enum):
    CAR = "car"
    MOTORCYCLE = "motorcycle"
    LARGE_VEHICLE = "large vehicle"

class Vehicle:
    def __init__(self, license_plate: str, vehicle_type: VehicleType):
        self.license_plate = license_plate
        self.vehicle_type = vehicle_type
        self.ticket_id = None
        self.parking_spot_id = None

    def assign_ticket(self, ticket_id: str):
        self.ticket_id = ticket_id

    def assign_parking_spot(self, spot_id: str) -> None:
        self.parking_spot_id = spot_id