
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

class Direction(str, Enum):
    UP= "up"
    DOWN= "down"
    IDLE= "idle"

class RequestType(str, Enum):
    INSIDE= "inside"
    OUTSIDE= "outside"

@dataclass(frozen=True, slots=True)
class Request:
    """
    Immutable request coming from either:
    - a hall call (request_type=OUTSIDE) that needs dispatching, or
    - a car call (request_type=INSIDE) that targets a specific elevator.
    """

    floor_num: int
    request_type: RequestType
    direction: Direction
    elevator_num: Optional[int] = None




    



