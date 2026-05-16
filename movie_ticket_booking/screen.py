import threading
from typing import Dict, List, Set

from movie_ticket_booking.show import Show


class Screen:
    screen_number: str
    theater_id: str
    total_seats: int
    shows: Dict[str, Show]

    def __init__(self, total_seats: int, screen_number: str, theater_id: str, show_timings: List[tuple[str, str]]):
        self.total_seats = total_seats
        self.screen_number = screen_number
        self.theater_id = theater_id
        self.shows = {f"{screen_number}-{show_timing}": Show(show_timing, f"{screen_number}-{show_timing}", total_seats, screen_number, movie_name) for show_timing, movie_name in show_timings}
        
    def get_all_shows(self) -> List[Show]:
        return list(self.shows.values())

    def get_show(self, show_number: str) -> Show:
        if show_number not in self.shows:
            raise ValueError("Show not found")
        return self.shows[show_number]
    
    def get_show_for_a_movie(self, movie_name: str) -> List[Show]:
        return [show for show in self.shows.values() if show.movie_name == movie_name]
    
    def get_all_movies(self) -> Set[str]:
        return set(show.movie_name for show in self.shows.values())
    
    def get_available_seats_for_a_show(self, number_of_seats: int, show_number: str) -> List[str]:
        if show_number not in self.shows:
            return []
        
        show = self.shows[show_number]
        return show.view_and_select_seats(number_of_seats)
    
    def is_show_available(self, show_number: str) -> bool:
        return show_number in self.shows