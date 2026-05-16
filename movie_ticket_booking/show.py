import threading
from typing import Dict, List, Union
import uuid

from movie_ticket_booking.booking import Booking


class Show:
    show_timing: str
    show_number: str
    screen_number: str
    movie_name: str
    total_seats: int
    seats: Dict[str, str] # seat_number -> booking_id
    booking: Dict[str, List[str]] # confirmation_id -> list of seat_numbers

    def __init__(self, show_timing: str, show_number: str, total_seats: int, screen_number: str, movie_name: str):
        self.show_timing = show_timing
        self.show_number = show_number
        self.total_seats = total_seats
        self.screen_number = screen_number
        self.movie_name = movie_name
        self.seats = {f"{show_timing}-{i}": None for i in range(1, total_seats + 1)}
        self.booking = {}
        self._lock = threading.RLock()

    def view_and_select_seats(self, number_of_seats: int) -> List[str]:
        with self._lock:
            available_seats = [seat_number for seat_number in self.seats if self.seats[seat_number] is None]

            if len(available_seats) < number_of_seats:
                raise ValueError("Not enough seats available")

            return available_seats[:number_of_seats]

    def book_seats(self, seat_numbers: List[str]) -> Union[str, None]:
        with self._lock:
            for seat_number in seat_numbers:
                
                if seat_number not in self.seats or self.seats[seat_number] is not None:
                    return None
                
            confirmation_id = uuid.uuid4().hex
            for seat_number in seat_numbers:
                self.seats[seat_number] = confirmation_id
            self.booking[confirmation_id] = seat_numbers
            return confirmation_id
        
    def cancel_booking(self, confirmation_id: str) -> bool:
        with self._lock:
            if confirmation_id not in self.booking:
                return False

            seat_numbers = self.booking[confirmation_id]
            for seat_number in seat_numbers:
                self.seats[seat_number] = None

            del self.booking[confirmation_id]
            return True
        