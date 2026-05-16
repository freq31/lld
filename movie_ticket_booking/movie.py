
from typing import Set


class Movie:
    name: str
    duration: float
    theaters: Set[str]

    def __init__(self, name: str, duration: float, theaters: Set[str]):
        self.name = name
        self.duration = duration
        self.theaters = theaters

    def get_all_theatres(self) -> Set[str]:
        return self.theaters