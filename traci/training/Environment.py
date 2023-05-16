import random

import traci

from controllers.Runner import Runner
from creators.NetworkCreator import NetworkCreator
from exceptions.TrafficAppException import TrafficAppException
from model.MoveType import MoveType
from model.State import State
from model.Street import Street
from training.Utils import Utils, directionMapper, getSumoBinary, allStreetTypes


class Environment:
    def __init__(self):
        self.networkCreator = None
        self.runner = None
        self.streets = {}
        self.lanesOnMoveType = {MoveType.NSR1: 0, MoveType.WER2: 0, MoveType.L1R1: 0, MoveType.L2R2: 0}
        self.avgLoadFactor = None
        self.remainingSteps = 0
        self.currentTotalLoad = None
        self.changingLoadsTime = 200

    def calculateAvgLoadFactor(self):
        if self.networkCreator is None:
            print("No network created!")
            return
        lanes = set()
        sumOfLoadFactor = 0
        for connection in self.networkCreator.connections:
            sumOfLoadFactor += connection.loadFactor
            lanes.add((connection.getFromEdge(), connection.fromLane))
        self.avgLoadFactor = sumOfLoadFactor / len(lanes)

    def createNetwork(self, streets):
        self.networkCreator = NetworkCreator(streets)
        self.networkCreator.createNetworkFile()
        self.runner = Runner(self.networkCreator.connections)
        self.numberOfLanes = 0

        for connection in self.networkCreator.connections:
            moveDirections = directionMapper[(connection.getFromEdge(), connection.getToEdge())]
            for moveDirection in moveDirections:
                self.lanesOnMoveType[moveDirection] = self.lanesOnMoveType[moveDirection] + 1
        self.calculateAvgLoadFactor()

    def createFrom(self, networkCreator, runner, streets):
        self.networkCreator = networkCreator
        self.runner = runner
        self.streets = streets
        self.calculateAvgLoadFactor()

    def reset(self):
        self.remainingSteps = Utils.TOTAL_ITERATION_STEPS.value
        ok = False
        while not ok:
            streets = {}
            for streetType in allStreetTypes:
                lanesIn = random.randint(1, 6)
                lanesOut = random.randint(3, 6)
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
        traci.start([sumoBinary, "-c", Utils.PATH_TO_SUMOCFG_FILE.value,
                     "--tripinfo-output", "app.tripinfo.xml", "--start", "--quit-on-end", "--waiting-time-memory", "1000"])

        return self.warmUp()

    def warmUp(self):
        self.runner.runForWarmUp(Utils.STEPS_UNTIL_FIRST_OBSERVATION.value)
        return self.getObservation()

    def nonTrainingStep(self, action):
        reward = self.runner.performStep(action * 2) / self.avgLoadFactor
        return self.getObservation(), reward

    def step(self, action):
        reward = self.runner.performStep(action * 2) / self.avgLoadFactor
        self.remainingSteps -= 1
        if self.remainingSteps % 10 == 0:
            print('Remaining steps:', self.remainingSteps)

        if self.remainingSteps % self.changingLoadsTime == 0:
            self.generateLoads()

        return self.getObservation(), reward, self.remainingSteps == 0, "no info"

    def getObservation(self):
        carsForMoveDirection = {(1, 2): 0.0, (1, 3): 0.0, (1, 4): 0.0, (2, 1): 0.0, (2, 3): 0.0, (2, 4): 0.0,
                                (3, 1): 0.0, (3, 2): 0.0, (3, 4): 0.0, (4, 1): 0.0, (4, 2): 0.0, (4, 3): 0.0}
        avgCarsForMoveDirection = {(1, 2): 0.0, (1, 3): 0.0, (1, 4): 0.0, (2, 1): 0.0, (2, 3): 0.0, (2, 4): 0.0,
                                   (3, 1): 0.0, (3, 2): 0.0, (3, 4): 0.0, (4, 1): 0.0, (4, 2): 0.0, (4, 3): 0.0}
        lanesForMoveDirection = {(1, 2): 0.0, (1, 3): 0.0, (1, 4): 0.0, (2, 1): 0.0, (2, 3): 0.0, (2, 4): 0.0,
                                 (3, 1): 0.0, (3, 2): 0.0, (3, 4): 0.0, (4, 1): 0.0, (4, 2): 0.0, (4, 3): 0.0}
        computedLanes = set()
        waitingForMoveDirection = {(1, 2): 0.0, (1, 3): 0.0, (1, 4): 0.0, (2, 1): 0.0, (2, 3): 0.0, (2, 4): 0.0,
                                   (3, 1): 0.0, (3, 2): 0.0, (3, 4): 0.0, (4, 1): 0.0, (4, 2): 0.0, (4, 3): 0.0}

        for connection in self.networkCreator.connections:
            if (connection.getFromEdge(), connection.fromLane) in computedLanes:
                continue
            computedLanes.add((connection.getFromEdge(), connection.fromLane))
            direction = (connection.getFromEdge(), connection.getToEdge())

            carsOnLane = self.collectCountDataForConnection(connection)
            lanesForMoveDirection[direction] += 1.0
            carsForMoveDirection[direction] += carsOnLane
            avgCarsForMoveDirection[direction] = carsForMoveDirection[direction] // lanesForMoveDirection[direction]

            waitingOnLane = self.collectWaitingDataForConnection(connection)
            waitingForMoveDirection[direction] += waitingOnLane

        return State(avgCarsForMoveDirection, waitingForMoveDirection,
                     self.runner.currentSemaphorePhase / Utils.NUMBER_OF_ACTIONS.value).stateList

    def collectCountDataForConnection(self, connection):
        return traci.lane.getLastStepVehicleNumber(connection.getLaneId())

    def collectWaitingDataForConnection(self, connection):
        totalWaiting = 0
        vehicles = traci.lane.getLastStepVehicleIDs(connection.getLaneId())

        for vehicle in vehicles:
            if traci.vehicle.getSpeed(vehicle) > 1.0:
                totalWaiting += traci.vehicle.getAccumulatedWaitingTime(vehicle)

        return totalWaiting

    def generateLoads(self):
        counterForWays = {}
        loadsForWays = {}
        for connection in self.networkCreator.connections:
            way = (connection.getFromEdge(), connection.getToEdge())
            if way not in counterForWays:
                counterForWays[way] = 0
            counterForWays[way] += 1
            loadsForWays[way] = (0.01 * random.randint(0, 20)) / counterForWays[way]

        for connection in self.networkCreator.connections:
            way = (connection.getFromEdge(), connection.getToEdge())
            connection.loadFactor = loadsForWays[way]

        self.calculateAvgLoadFactor()
