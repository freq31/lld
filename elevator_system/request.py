
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

class Direction(str, Enum):
    UP= "up"
    DOWN= "down"
    IDLE= "idle"

class RequestType(str, Enum):
    PICKUP= "pickup"
    DROPOFF= "dropoff"
    PICKDOWN= "pickdown"

@dataclass(frozen=True, slots=True)
class Request:
    floor_num: int
    request_type: RequestType
    elevator_num: Optional[int] = None




    



