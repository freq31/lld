
from traitlets import Union
from movie_ticket_booking.booking import Booking
from movie_ticket_booking.movie import Movie
from movie_ticket_booking.payment_interface import PaymentInterface
from movie_ticket_booking.show import Show
from movie_ticket_booking.theater import Theater


class BookingManager:
    payment_interface: PaymentInterface
    theaters: dict[str, Theater]
    bookings: dict[str, Booking]
    movies: dict[str,Movie]

    def search_movies(self, movie_title: str) -> list[Movie]:
        return [movie for movie in self.movies.values() if movie_title.lower() in movie.name.lower()]
    
    def get_movies_in_a_theater(self, theater_id: str) -> list[Movie]:
        if theater_id not in self.theaters:
            return []
        
        theater = self.theaters[theater_id]
        movies = theater.get_all_movies()
        return list(movies)
    
    def get_all_theatres(self) -> list[Theater]:
        return list(self.theaters.values())
    
    def get_all_movies(self) -> list[Movie]:
        return list(self.movies.values())
    
    def get_all_shows_for_a_movie_in_a_theater(self, movie_name: str, theater_id: str) -> list[Show]:
        if theater_id not in self.theaters:
            return []
        
        theater = self.theaters[theater_id]
        shows = theater.get_all_shows_for_a_movie(movie_name)
        return shows
    
    def get_available_seats_for_a_show(self, theater_id: str, show_number: str, number_of_seats: int) -> list[str]:
        if theater_id not in self.theaters:
            return []
        
        theater = self.theaters[theater_id]
        for screen in theater.screens.values():
            seats = screen.get_available_seats_for_a_show(number_of_seats, show_number)
            if seats:
                return seats
        return []
    
    def book_seats(self, theater_id: str, show_number: str, seat_numbers: list[str]) -> Union[Booking, None]:
        if theater_id not in self.theaters:
            raise ValueError("Theater not found")
        
        theater = self.theaters[theater_id]

        for screen in theater.screens.values():
            if screen.is_show_available(show_number):
                booking = Booking(show_number, theater_id, seat_numbers)
                payment_result = self.payment_interface.process_payment(booking, payment_details={})

                if not payment_result:
                    raise ValueError("Payment failed")
                
                show = screen.get_show(show_number)
                confirmation_id = show.book_seats(seat_numbers)

                if confirmation_id is None:
                    self.payment_interface.reverse_payment(booking)
                    raise ValueError("Seats not available")
                
                booking.confirm_booking(confirmation_id)
                self.bookings[booking.confirmation_id] = booking
                return booking
            

    def cancel_booking(self, confirmation_id: str) -> bool:
        if confirmation_id not in self.bookings:
            raise ValueError("Booking not found")
        
        booking = self.bookings[confirmation_id]

        if booking.theater_id not in self.theaters:
            raise ValueError("Theater not found")
        
        theater = self.theaters[booking.theater_id]

        for screen in theater.screens.values():
            if screen.is_show_available(booking.show_number):
                show = screen.get_show(booking.show_number)
                cancel_result = show.cancel_booking(confirmation_id)

                if not cancel_result:
                    raise ValueError("Cancellation failed")
                
                payment_reverse_result = self.payment_interface.reverse_payment(booking)

                if not payment_reverse_result:
                    raise ValueError("Payment reversal failed")
                
                del self.bookings[confirmation_id]
                return True
            
        return False

    
