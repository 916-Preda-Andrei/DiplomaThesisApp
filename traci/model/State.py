class State:

    def __init__(self, carsForLane, waitingForLane, queueForLane, phase):
        self.stateList = []
        cars = []
        waiting = []
        queue = []
        for street in range(1, 5):
            for lane in range(0, 3):
                laneId = "E_" + str(street) + "_0_" + str(lane)
                cars.append(carsForLane[laneId])
                waiting.append(waitingForLane[laneId])
                queue.append(queueForLane[laneId])
        self.stateList.extend(cars)
        self.stateList.extend(waiting)
        self.stateList.extend(queue)
        self.stateList.append(phase + 1.0)
