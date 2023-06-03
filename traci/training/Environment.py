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
        self.streets = {}
        self.lanesOnMoveType = {MoveType.NSR1: 0, MoveType.WER2: 0, MoveType.L1R1: 0, MoveType.L2R2: 0}
        self.scheduleMoveType = {}
        self.totalLoadFactor = None
        self.remainingSteps = 0
        self.changingLoadsTime = 100

    def setSchedule(self, schedule):
        self.scheduleMoveType = {MoveType.NSR1: schedule[0], MoveType.WER2: schedule[1], MoveType.L1R1: schedule[2], MoveType.L2R2: schedule[3]}

    def calculateTotalLoadFactor(self):
        if self.networkCreator is None:
            print("No network created!")
            return

        self.totalLoadFactor = 0
        for connection in self.networkCreator.connections:
            self.totalLoadFactor += connection.loadFactor

    def createNetwork(self, streets):
        self.networkCreator = NetworkCreator(streets)
        self.networkCreator.createNetworkFile()
        self.runner = Runner(self.networkCreator.connections)

        for connection in self.networkCreator.connections:
            moveDirections = directionMapper[(connection.getFromEdge(), connection.getToEdge())]
            for moveDirection in moveDirections:
                self.lanesOnMoveType[moveDirection] = self.lanesOnMoveType[moveDirection] + 1
        self.calculateTotalLoadFactor()

    def createFrom(self, networkCreator, runner, streets):
        self.networkCreator = networkCreator
        self.runner = runner
        self.streets = streets
        self.calculateTotalLoadFactor()

    def reset(self, preTraining=False, training=False):
        self.remainingSteps = Utils.TOTAL_ITERATION_STEPS.value
        ok = False
        while not ok:
            streets = {}
            for streetType in allStreetTypes:
                lanesIn = 1
                lanesOut = 3
                streets[streetType] = Street(streetType, lanesIn, lanesOut)

            try:
                self.createNetwork(streets)
                ok = True
                self.streets = streets
            except TrafficAppException:
                pass

        if self.runner is not None and self.runner.running:
            raise TrafficAppException("SUMO already started")

        if self.networkCreator is None:
            raise TrafficAppException("No network has been created yet")

        if self.runner is None:
            raise TrafficAppException("Runner not working!")

        # self.generateLoads()

        sumoFile = Utils.PATH_TO_SUMOCFG_FILE.value
        if training:
            sumoFile = Utils.PATH_TO_SUMOCFG_FILE_TRAINING.value
            if preTraining:
                sumoFile = Utils.PATH_TO_SUMOCFG_FILE_PRE_TRAINING.value

        sumoBinary = getSumoBinary()
        traci.start(
            [sumoBinary, "-c", sumoFile, "--start", "--quit-on-end", "--waiting-time-memory",
             "1000"])

        return self.warmUp()

    def warmUp(self):
        self.runner.runForWarmUp(Utils.STEPS_UNTIL_FIRST_OBSERVATION.value)
        return self.getObservation()

    def nonTrainingStep(self, action):
        reward = self.runner.performStep(action * 2)
        return self.getObservation(), reward

    def step(self, action):
        reward = self.runner.performStep(action * 2)
        self.remainingSteps -= 1
        # if (self.remainingSteps % self.changingLoadsTime) == 0:
        #     self.generateLoads()
        return self.getObservation(), reward, self.remainingSteps == 0

    def getObservation(self):
        carsForLane = {}
        waitingForLane = {}
        queueForLane = {}

        computedLanes = set()

        for connection in self.networkCreator.connections:
            if (connection.getFromEdge(), connection.fromLane) in computedLanes:
                continue
            computedLanes.add((connection.getFromEdge(), connection.fromLane))

            laneId = connection.getLaneId()
            carsForLane[laneId] = collectCountDataForLane(laneId)
            waitingForLane[laneId] = collectWaitingDataForLane(laneId)
            queueForLane[laneId] = collectQueueDataForLane(laneId)

        return State(carsForLane, waitingForLane, queueForLane, self.runner.currentSemaphorePhase // 2).stateList

    def generateLoads(self):
        counterForWays = {}
        loadsForWays = {}
        for connection in self.networkCreator.connections:
            way = (connection.getFromEdge(), connection.getToEdge())
            if way not in counterForWays:
                counterForWays[way] = 0
            counterForWays[way] += 1
            loadsForWays[way] = (0.01 * random.randint(0, 10)) / counterForWays[way]

        for connection in self.networkCreator.connections:
            way = (connection.getFromEdge(), connection.getToEdge())
            connection.loadFactor = loadsForWays[way]

        self.runner.connections = self.networkCreator.connections
