from typing import Dict, List, Set

from movie_ticket_booking.screen import Screen
from movie_ticket_booking.show import Show


class Theater:
    name: str
    location: str
    theater_id: str
    screens: Dict[str, Screen]
    movies: Set[str]

    def __init__(self, name: str, location: str, theater_id: str, screen_details: List[tuple[int, List[tuple[str, str]]]]):
        self.name = name
        self.location = location
        self.theater_id = theater_id
        self.movies = set()
        self.screens = {i: Screen(screen_details[i][0], i, self.theater_id, screen_details[i][1]) for i in range(len(screen_details))}
        for screen in self.screens.values():
            screen_movies = screen.get_all_movies()
            self.movies.update(screen_movies)

    def get_all_shows_for_a_movie(self, movie_name: str) -> List[Show]:
        shows= []
        for screen in self.screens.values():
            shows.extend(screen.get_show_for_a_movie(movie_name))
        return shows
    
    def get_all_movies(self) -> Set[str]:
        return self.movies
    
