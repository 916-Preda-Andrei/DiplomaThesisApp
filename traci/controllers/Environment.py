from controllers.Runner import Runner
from creators.NetworkCreator import NetworkCreator
from model.State import State
from Utils import Utils


class Environment:
    def __init__(self):
        self.networkCreator = None
        self.runner = None
        self.remainingSteps = 0

    def createNetwork(self):
        self.networkCreator = NetworkCreator()
        self.networkCreator.createNetworkFile()
        self.runner = Runner(self.networkCreator.connections)

    def createFrom(self, networkCreator, runner):
        self.networkCreator = networkCreator
        self.runner = runner

    def reset(self, preTraining=False, training=False):
        self.remainingSteps = Utils.TOTAL_ITERATION_STEPS_PRE_TRAINING.value if preTraining else Utils.TOTAL_ITERATION_STEPS.value
        self.createNetwork()

        if training:
            sumoFile = Utils.PATH_TO_SUMOCFG_FILE_TRAINING.value
        elif preTraining:
            sumoFile = Utils.PATH_TO_SUMOCFG_FILE_PRE_TRAINING.value
        else:
            sumoFile = Utils.PATH_TO_SUMOCFG_FILE.value

        self.runner.startSimulator(sumoFile)

        return self.warmUp()

    def warmUp(self):
        self.runner.runForWarmUp(Utils.STEPS_UNTIL_FIRST_OBSERVATION.value)
        return self.getObservation()

    def nonTrainingStep(self, action):
        reward = self.runner.performNonTrainingStep(action * 2)
        return self.getObservation(), reward

    def step(self, action):
        reward = self.runner.performStep(action * 2)
        self.remainingSteps -= 1
        return self.getObservation(), reward, self.remainingSteps == 0

    def getObservation(self):
        carsForLane = {}
        waitingForLane = {}
        queueForLane = {}

        computedLanes = set()

        for connection in self.networkCreator.connections:
            if (connection.fromEdge, connection.fromLane) in computedLanes:
                continue
            computedLanes.add((connection.fromEdge, connection.fromLane))

            laneId = connection.laneId
            carsForLane[laneId] = self.runner.collectCountDataForLane(laneId)
            waitingForLane[laneId] = self.runner.collectWaitingDataForLane(laneId)
            queueForLane[laneId] = self.runner.collectQueueDataForLane(laneId)

        return State(carsForLane, waitingForLane, queueForLane, self.runner.currentSemaphorePhase // 2,
                     self.runner.freshChanged).stateList
