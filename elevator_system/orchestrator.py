from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from elevator_system.elevator import Elevator, ElevatorState  # ElevatorState: IDLE, MOVING
from elevator_system.floors import Floors
from elevator_system.request import Direction, Request, RequestType


class DispatchStrategy(ABC):
    @abstractmethod
    def choose_elevator(self, elevators: list[Elevator], request: Request) -> Elevator:
        raise NotImplementedError


class NearestOnDirectionStrategy(DispatchStrategy):
    """
    Simple SDE-2-friendly heuristic:
    - Prefer idle elevators first
    - Prefer elevators already moving toward the requested direction and passing the floor
    - Then minimize distance
    """

    def choose_elevator(self, elevators: list[Elevator], request: Request) -> Elevator:
        def effective_request_dir_for_elevator(e: Elevator) -> Direction:
            # If the request direction is unknown, infer based on relative position to this elevator.
            if request.direction != Direction.IDLE:
                return request.direction
            return Direction.UP if request.floor_num > e.current_floor.floor_num else Direction.DOWN

        def is_on_the_way(e: Elevator) -> bool:
            if e.state == ElevatorState.IDLE:
                return True

            req_dir = effective_request_dir_for_elevator(e)
            if req_dir == Direction.UP:
                return e.current_dir == Direction.UP and e.current_floor.floor_num <= request.floor_num
            if req_dir == Direction.DOWN:
                return e.current_dir == Direction.DOWN and e.current_floor.floor_num >= request.floor_num
            return True

        def rank(e: Elevator):
            # 0 for idle elevators, 1 for moving elevators (idle first)
            idle_first = e.state != ElevatorState.IDLE
            req_dir = effective_request_dir_for_elevator(e)
            return (
                idle_first,
                not is_on_the_way(e),
                e.current_dir != req_dir,
                abs(e.current_floor.floor_num - request.floor_num),
            )

        return min(elevators, key=rank)


class ElevatorManager:
    elevators: list[Elevator]
    floors: Floors
    def __init__(
        self,
        number_of_elevators: int,
        number_of_floors: int,
        *,
        dispatch_strategy: Optional[DispatchStrategy] = None,
    ):
        self.elevators = []
        self.floors = Floors(number_of_floors)
        self.number_of_elevators = number_of_elevators
        self.dispatch_strategy: DispatchStrategy = dispatch_strategy or NearestOnDirectionStrategy()

        for i in range(number_of_elevators):
            self.elevators.append(Elevator(i, self.floors))

    def handle_request(self, request: Request):
        if request.request_type == RequestType.INSIDE:
            # Car call must target a specific elevator.
            if request.elevator_num is None:
                raise ValueError("INSIDE request must include elevator_num")
            if 0 <= request.elevator_num < self.number_of_elevators:
                self.elevators[request.elevator_num].handle_request(request)
            return

        # OUTSIDE request (hall call) -> either dispatch or route to provided elevator.
        if request.elevator_num is not None and 0 <= request.elevator_num < self.number_of_elevators:
            self.elevators[request.elevator_num].handle_request(request)
            return

        best = self.dispatch_strategy.choose_elevator(self.elevators, request)
        self.elevators[best.num].handle_request(request)

    def next(self):
        served: list[tuple[int, int]] = []
        for elevator in self.elevators:
            served_floor = elevator.next()
            if served_floor is not None:
                served.append((elevator.num, served_floor))
        return served