class Floor:
    def __init__(self, floor_num: int):
        self.floor_num = floor_num
        self.is_end= False
        self.is_start= False
    
    def set_end(self):
        self.is_end= True

    def set_start(self):
        self.is_start= True

class Floors:
    def __init__(self, number_of_floors: int):
        self.floors: list[Floor] = []
        self.number_of_floors= number_of_floors
        for i in range(number_of_floors):
            self.floors.append(Floor(i))
        self.floors[0].set_start()
        self.floors[number_of_floors-1].set_end()
        
    def get_floor(self, floor_num: int):
        if(floor_num< self.number_of_floors and floor_num>=0):
            return self.floors[floor_num]
        return None


