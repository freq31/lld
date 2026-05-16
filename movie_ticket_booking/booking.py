
import uuid

class Booking:
    booking_id: str
    confirmation_id: str
    show_number: str
    theater_id: str
    seat_numbers: list[str]

    def __init__(self, show_number: str, theater_id: str, seat_numbers: list[str]):
        self.booking_id = uuid.uuid4().hex
        self.confirmation_id = None
        self.show_number = show_number
        self.theater_id = theater_id
        self.seat_numbers = seat_numbers

    def confirm_booking(self, confirmation_id: str):
        self.confirmation_id = confirmation_id