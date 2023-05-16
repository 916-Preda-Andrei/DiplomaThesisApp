from training.Utils import allMoveTypes


class State:

    def __init__(self, avgCarsForMoveDirection, waitingForMoveDirection, phase):
        self.stateList = []
        self.stateList.extend(list(avgCarsForMoveDirection.values()))
        self.stateList.extend(list(waitingForMoveDirection.values()))
        self.stateList.append(phase)
