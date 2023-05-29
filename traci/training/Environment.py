import random

import traci

from controllers.Runner import Runner
from creators.NetworkCreator import NetworkCreator
from exceptions.TrafficAppException import TrafficAppException
from model.MoveType import MoveType
from model.State import State
from model.Street import Street
from training.Utils import Utils, directionMapper, getSumoBinary, allStreetTypes


def collectCountDataForConnection(connection):
    counter = 0
    vehicles = traci.lane.getLastStepVehicleIDs(connection.getLaneId())
    for vehicle in vehicles:
        x, y = traci.vehicle.getPosition(vehicle)
        if (abs(x - 500.0) + abs(y - 500.0)) <= Utils.DETECT_CARS_DISTANCE.value:
            counter += 1
    return counter


class Environment:
    def __init__(self):
        self.networkCreator = None
        self.runner = None
        self.streets = {}
        self.lanesOnMoveType = {MoveType.NSR1: 0, MoveType.WER2: 0, MoveType.L1R1: 0, MoveType.L2R2: 0}
        self.totalLoadFactor = None
        self.remainingSteps = 0
        self.changingLoadsTime = 100

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

    def reset(self):
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

        self.generateLoads()

        sumoBinary = getSumoBinary()
        traci.start(
            [sumoBinary, "-c", Utils.PATH_TO_SUMOCFG_FILE.value, "--start", "--quit-on-end", "--waiting-time-memory",
             "10000"])

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
        if (self.remainingSteps % self.changingLoadsTime) == 0:
            self.generateLoads()
        return self.getObservation(), reward, self.remainingSteps == 0

    def getObservation(self):
        carsForMoveType = {MoveType.NSR1: 0, MoveType.WER2: 0, MoveType.L1R1: 0, MoveType.L2R2: 0}
        computedLanes = set()

        for connection in self.networkCreator.connections:
            if (connection.getFromEdge(), connection.fromLane) in computedLanes:
                continue
            computedLanes.add((connection.getFromEdge(), connection.fromLane))
            direction = (connection.getFromEdge(), connection.getToEdge())

            carsOnLane = collectCountDataForConnection(connection)
            for moveType in directionMapper[direction]:
                carsForMoveType[moveType] += carsOnLane

        return State(carsForMoveType, self.runner.currentSemaphorePhase // 2).stateList

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
