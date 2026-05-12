import datetime
from enum import Enum
from typing import Optional

from parking_lot_system.vehicle import VehicleType

class TicketStatus(str, Enum):
    ACTIVE = "active"
    PAID = "paid"
    EXPIRED = "expired"

class Ticket:
    def __init__(self, ticket_id: str, vehicle_number: str, vehicle_type: VehicleType, spot_id: str):
        self.ticket_id = ticket_id
        self.vehicle_number = vehicle_number
        self.vehicle_type = vehicle_type
        self.spot_id = spot_id
        self.entry_time = datetime.datetime.now()
        self.exit_time = None
        self.status = TicketStatus.ACTIVE

    def is_valid(self) -> bool:
        return self.status == TicketStatus.ACTIVE

    def update_status(self, new_status: TicketStatus):
        self.status = new_status

    def set_exit_time(self, when: Optional[datetime.datetime] = None) -> None:
        self.exit_time = when if when is not None else datetime.datetime.now()