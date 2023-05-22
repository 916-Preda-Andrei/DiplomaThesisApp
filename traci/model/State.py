from training.Utils import Utils


class State:

    def __init__(self, carsForMoveType, phase):
        self.stateList = []
        for phase in Utils.initialSemaphorePhases.value:
            self.stateList.append(carsForMoveType[phase])
        for i in range(Utils.NUMBER_OF_ACTIONS.value):
            self.stateList.append(1) if phase == i else self.stateList.append(0)
