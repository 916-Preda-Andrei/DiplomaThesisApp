import random

import traci

from controllers.Runner import Runner
from creators.NetworkCreator import NetworkCreator
from exceptions.TrafficAppException import TrafficAppException
from model.MoveType import MoveType
from model.State import State
from model.Street import Street
from training.Utils import Utils, directionMapper, getSumoBinary, allStreetTypes


def collectCountDataForLane(lane):
    return traci.lane.getLastStepVehicleNumber(lane)

def collectWaitingDataForLane(lane):
    return traci.lane.getWaitingTime(lane) / 60.0

def collectQueueDataForLane(lane):
    return traci.lane.getLastStepHaltingNumber(lane)


class Environment:
    def __init__(self):
        self.networkCreator = None
        self.runner = None
        self.lanesOnMoveType = {MoveType.NSR1: 0, MoveType.WER2: 0, MoveType.L1R1: 0, MoveType.L2R2: 0}
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

        sumoBinary = getSumoBinary()
        traci.start([sumoBinary, "-c", sumoFile, "--start", "--quit-on-end", "--waiting-time-memory", "10000"])

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
            carsForLane[laneId] = collectCountDataForLane(laneId)
            waitingForLane[laneId] = collectWaitingDataForLane(laneId)
            queueForLane[laneId] = collectQueueDataForLane(laneId)

        return State(carsForLane, waitingForLane, queueForLane, self.runner.currentSemaphorePhase // 2, self.runner.freshChanged).stateList
