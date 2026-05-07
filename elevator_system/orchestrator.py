from __future__ import annotations

from abc import ABC, abstractmethod
from queue import Queue
from typing import Optional

from elevator_system.elevator import Elevator, ElevatorState  # ElevatorState: IDLE, MOVING
from elevator_system.floors import Floors
from elevator_system.request import Direction, Request, RequestType


class DispatchStrategy(ABC):
    @abstractmethod
    def choose_elevator(self, elevators: list[Elevator], request: Request) -> Elevator:
        raise NotImplementedError


class ScanDispatchStrategy(DispatchStrategy):
    """
    Simple SDE-2-friendly heuristic:
    - Prefer idle elevators first
    - Prefer elevators already moving toward the requested direction and passing the floor
    - Then minimize distance
    """

    def choose_elevator(self, elevators: list[Elevator], request: Request) -> Elevator:
        def is_on_the_way(e: Elevator) -> bool:
            if e.state == ElevatorState.IDLE:
                return True

            if request.request_type == RequestType.PICKUP:
                return e.current_dir == Direction.UP and e.current_floor.floor_num <= request.floor_num
            elif request.request_type == RequestType.DROPOFF:
                if e.current_floor.floor_num>= request.floor_num:
                    return e.current_dir == Direction.DOWN
                elif e.current_floor.floor_num< request.floor_num:
                    return e.current_dir == Direction.UP
                return True
            elif request.request_type == RequestType.PICKDOWN:
                return e.current_dir == Direction.DOWN and e.current_floor.floor_num >= request.floor_num
            return True

        def rank(e: Elevator):
            # 0 for idle elevators, 1 for moving elevators (idle first)
            idle_first = e.state != ElevatorState.IDLE
            return (
                idle_first , #idle first
                not is_on_the_way(e), #on the way next
                abs(e.current_floor.floor_num - request.floor_num), #nearest
            )
        return min(elevators, key=rank)

class SSTFDispatchStrategy(DispatchStrategy):
    def choose_elevator(self, elevators: list[Elevator], request: Request) -> Elevator:

        def rank(e: Elevator):
            return (
                abs(e.current_floor.floor_num - request.floor_num), #nearest
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
        self.dispatch_strategy: DispatchStrategy = dispatch_strategy or ScanDispatchStrategy()
        #thread safe request queue
        self.request_queue = Queue(maxsize=100)

        for i in range(number_of_elevators):
            self.elevators.append(Elevator(i, self.floors))

    def add_request(self, request: Request):
        self.request_queue.put(request)

    def handle_request(self, request: Request):
        if request.request_type == RequestType.DROPOFF:
            if request.elevator_num is None:
                raise ValueError("DROPOFF request must include elevator_num")
            if 0 <= request.elevator_num < self.number_of_elevators:
                self.elevators[request.elevator_num].handle_request(request)
                return
            else:
                raise ValueError("Invalid elevator_num")

        def can_serve(e: Elevator):
            if request.floor_num not in [0, 5, 9]:
                return not e.is_vip_express
            return True
            
        eligible_elevators = [e for e in self.elevators if can_serve(e)]
        best = self.dispatch_strategy.choose_elevator(eligible_elevators, request)
        self.elevators[best.num].handle_request(request)

    def next(self):
        
        #handle requests in the queue 1st before handling requests in the elevators
        while not self.request_queue.empty():
            request = self.request_queue.get()
            self.handle_request(request)

        #handle requests in the elevators
        served: list[tuple[int, int]] = []
        for elevator in self.elevators:
            served_floor = elevator.next()
            if served_floor is not None:
                served.append((elevator.num, served_floor))
        return served