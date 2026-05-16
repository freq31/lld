

from movie_ticket_booking.booking import Booking


class PaymentInterface:
    def process_payment(self, booking: Booking, payment_details) -> bool:
        return True
    
    def reverse_payment(self, booking: Booking) -> bool:
        return True