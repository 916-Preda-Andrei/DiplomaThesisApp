
class State:

    def __init__(self, carsForMoveDirection, lanesForMoveDirection, phase):
        self.stateList = []
        self.stateList.extend(list(carsForMoveDirection.values()))
        self.stateList.extend(list(lanesForMoveDirection.values()))
        self.stateList.append(phase)
