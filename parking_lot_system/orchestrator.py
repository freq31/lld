import datetime
import math
import threading
import uuid
from typing import List, Union
from parking_lot_system.parking_spot import ParkingSpot
from parking_lot_system.payment_orchestrator import PaymentOrchestrator
from parking_lot_system.ticket import Ticket, TicketStatus
from parking_lot_system.vehicle import Vehicle, VehicleType


class ParkingLotManager:
    def __init__(self, compact_spots: int, large_spots: int, motorcycle_spots: int, compact_hr: float, large_hr: float, motorcycle_hr: float):
        self.vehicle_type_spot_map: dict[VehicleType, List[ParkingSpot]] = {}
        self.vehicle_type_hr_map: dict[VehicleType, float] = {}

        self.vehicle_type_spot_map[VehicleType.CAR] = [ParkingSpot(str(uuid.uuid4()), VehicleType.CAR) for i in range(compact_spots)]
        self.vehicle_type_hr_map[VehicleType.CAR] = compact_hr

        self.vehicle_type_spot_map[VehicleType.LARGE_VEHICLE] = [ParkingSpot(str(uuid.uuid4()), VehicleType.LARGE_VEHICLE) for i in range(large_spots)]
        self.vehicle_type_hr_map[VehicleType.LARGE_VEHICLE] = large_hr

        self.vehicle_type_spot_map[VehicleType.MOTORCYCLE] = [ParkingSpot(str(uuid.uuid4()), VehicleType.MOTORCYCLE) for i in range(motorcycle_spots)]
        self.vehicle_type_hr_map[VehicleType.MOTORCYCLE] = motorcycle_hr

        self.tickets: dict[str, Ticket] = {}
        self.occupied_spots: dict[str, ParkingSpot] = {}
        # Serializes check-in / check-out vs shared maps and spot occupancy.
        self._lock = threading.RLock()

    def check_in_vehicle(self, vehicle: Vehicle) -> Union[Ticket, None]:
        with self._lock:
            if vehicle.vehicle_type not in self.vehicle_type_spot_map:
                return None

            spots = self.vehicle_type_spot_map[vehicle.vehicle_type]
            for spot in spots:
                if spot.park_vehicle(vehicle):
                    return self.assign_vehicle(vehicle, spot)

            return None

    def assign_vehicle(self, vehicle: Vehicle, spot: ParkingSpot) -> Union[Ticket, None]:
        ticket = self.generate_ticket(vehicle, spot.spot_id)
        self.tickets[ticket.ticket_id] = ticket
        vehicle.assign_ticket(ticket.ticket_id)
        vehicle.assign_parking_spot(spot.spot_id)
        self.occupied_spots[spot.spot_id] = spot
        return ticket
    
    def generate_ticket(self, vehicle: Vehicle, spot_id: str) -> Ticket:
        return Ticket(
            ticket_id=f"{vehicle.license_plate}_{datetime.datetime.now()}",
            vehicle_number=vehicle.license_plate,
            vehicle_type=vehicle.vehicle_type,
            spot_id=spot_id,
        )

    def check_out_vehicle(self, ticket_id: str) -> bool:
        with self._lock:
            if ticket_id not in self.tickets:
                return False

            ticket = self.tickets[ticket_id]

            if not ticket.is_valid():
                return False

            spot_id = ticket.spot_id
            if spot_id not in self.occupied_spots:
                return False

            spot = self.occupied_spots[spot_id]
            if spot is None:
                return False

            exit_at = datetime.datetime.now()
            total_rate = self.compute_parking_charge(ticket, exit_at)

            if PaymentOrchestrator.process_payment(total_rate):
                ticket.set_exit_time(exit_at)
                ticket.update_status(TicketStatus.PAID)
                self.occupied_spots.pop(spot_id, None)
                spot.remove_vehicle()
                ticket.update_status(TicketStatus.EXPIRED)
                return True

            return False
    
    def compute_total_hours(self, ticket: Ticket, exit_time: datetime.datetime) -> int:
        return max(1, math.ceil((exit_time - ticket.entry_time).total_seconds() / 3600))  # Duration in hours
    
    def compute_parking_charge(self, ticket: Ticket, exit_time: datetime.datetime) -> float:
        total_hours = self.compute_total_hours(ticket, exit_time)
        
        if ticket.vehicle_type not in self.vehicle_type_hr_map:
            raise ValueError("Vehicle type not found")
        
        hourly_rate = self.vehicle_type_hr_map[ticket.vehicle_type]
        return total_hours * hourly_rate