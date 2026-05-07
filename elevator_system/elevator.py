

from __future__ import annotations

from enum import Enum
from typing import Optional

from elevator_system.floors import Floor, Floors
from elevator_system.request import Direction, Request, RequestType


class ElevatorState(str, Enum):
    IDLE = "idle"
    MOVING = "moving"


class Elevator:
    """
    Local elevator state:
    - Keeps deterministic pending targets (direction-aware)
    - Uses a simple state machine: IDLE -> MOVING
    - Serves all pending targets at the current floor on arrival.
    """

    def __init__(
        self,
        elevator_num: int,
        floors: Floors,
        *,
        is_vip_express: bool = False,
        start_floor: int = 0,
    ):
        self.num = elevator_num
        self.floors = floors
        self.is_vip_express = is_vip_express
        start = self.floors.get_floor(start_floor)
        if start is None:
            raise ValueError(f"Invalid start floor: {start_floor}")
        self.current_floor: Floor = start

        # When IDLE, we set current_dir to Direction.IDLE for easier dispatch ranking.
        self.state: ElevatorState = ElevatorState.IDLE
        self.current_dir: Direction = Direction.IDLE

        # Pending targets split by intended travel direction.
        self._pending_up: set[int] = set()
        self._pending_down: set[int] = set()

    def _is_valid_floor_num(self, floor_num: int) -> bool:
        return 0 <= floor_num < self.floors.number_of_floors

    def remove_request(self, request: Request) -> None:
        self._pending_up.discard(request.floor_num)
        self._pending_down.discard(request.floor_num)

    def handle_request(self, request: Request) -> None:
        if not self._is_valid_floor_num(request.floor_num):
            return
        if request.floor_num == self.current_floor.floor_num:
            return

        direction = None

        if request.request_type in [RequestType.PICKUP, RequestType.DROPOFF] :
            direction = Direction.UP if request.floor_num > self.current_floor.floor_num else Direction.DOWN

        elif request.request_type == RequestType.PICKDOWN:
            direction = Direction.DOWN if request.floor_num < self.current_floor.floor_num else Direction.UP
        else:
            return

        if direction == Direction.UP:
            self._pending_up.add(request.floor_num)
        elif direction == Direction.DOWN:
            self._pending_down.add(request.floor_num)


    def _has_pending(self) -> bool:
        return bool(self._pending_up or self._pending_down)

    def _pick_next_direction_from_idle(self) -> Optional[Direction]:
        cur = self.current_floor.floor_num

        if not self._has_pending():
            return None

        # Choose nearest pending floor overall, tie-breaking toward UP for determinism.
        candidates: list[tuple[int, Direction, int]] = []
        for f in self._pending_up:
            candidates.append((abs(f - cur), Direction.UP, f))
        for f in self._pending_down:
            candidates.append((abs(f - cur), Direction.DOWN, f))

        candidates.sort(key=lambda x: (x[0], 0 if x[1] == Direction.UP else 1))
        _, best_dir, _ = candidates[0]
        return best_dir

    def _pick_next_direction_while_moving(self) -> Optional[Direction]:
        """
        LOOK-like behavior:
        - If there are pending targets ahead in the current direction, keep moving.
        - Otherwise, switch direction if there are targets in the opposite direction.
        - Otherwise, become IDLE.
        """
        cur = self.current_floor.floor_num

        if self.current_dir == Direction.UP:
            if any(f > cur for f in self._pending_up):
                return Direction.UP
            if any(f < cur for f in self._pending_down):
                return Direction.DOWN
        elif self.current_dir == Direction.DOWN:
            if any(f < cur for f in self._pending_down):
                return Direction.DOWN
            if any(f > cur for f in self._pending_up):
                return Direction.UP

        return None

    def _has_stop_at_current_floor(self) -> bool:
        cur = self.current_floor.floor_num
        return cur in self._pending_up or cur in self._pending_down

    def _serve_current_floor(self) -> None:
        cur = self.current_floor.floor_num
        self._pending_up.discard(cur)
        self._pending_down.discard(cur)

    def next(self) -> Optional[int]:
        """
        Advances the elevator by one tick.
        Returns the served floor number on arrival, else None.
        """
        if self.state == ElevatorState.IDLE:
            next_dir = self._pick_next_direction_from_idle()
            if next_dir is None:
                return None
            self.current_dir = next_dir
            self.state = ElevatorState.MOVING
        elif self.state == ElevatorState.MOVING:
            next_dir = self._pick_next_direction_while_moving()
            if next_dir is None:
                self.state = ElevatorState.IDLE
                self.current_dir = Direction.IDLE
                return None
            self.current_dir = next_dir
        
        # MOVING: advance one floor in the current direction.
        cur = self.current_floor.floor_num
        step = 1 if self.current_dir == Direction.UP else -1
        next_floor_num = cur + step

        next_floor = self.floors.get_floor(next_floor_num)
        if next_floor is None:
            return None
        self.current_floor = next_floor

        if self._has_stop_at_current_floor():
            self._serve_current_floor()
            return self.current_floor.floor_num

        return None

    def is_empty(self) -> bool:
        return not self._has_pending()

