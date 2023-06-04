import random
import re
import sys

import traci
import traci.constants as tc

from training.Utils import Utils

LANE_OUT_REGEX = "^E_[1234]_0_[012345]$"


class Runner:
    def __init__(self, connections):
        self.connections = connections
        self.running = False
        self.currentSemaphorePhase = 0
        self.vehiclesCount = 0
        self.vehiclesLeft = set()
        self.changedSemaphore = None
        self.enterTime = {}

    def setSemaphore(self, selectedPhase):
        rewards = 0.0
        if selectedPhase != self.currentSemaphorePhase:
            self.changedSemaphore = True
            self.currentSemaphorePhase += 1
            traci.trafficlight.setPhase("0", str(self.currentSemaphorePhase))

            changed = True
            for i in range(Utils.YELLOW_LIGHT.value):
                traci.simulationStep()
                rewards += self.getReward(changed)
                changed = False
            self.currentSemaphorePhase = selectedPhase
        else:
            self.changedSemaphore = False
        traci.trafficlight.setPhase("0", str(self.currentSemaphorePhase))
        return rewards

    def addVehicles(self):
        for connection in self.connections:
            randomNumber = random.random()
            if randomNumber < connection.loadFactor:
                vehicleId = "V" + str(self.vehiclesCount)
                traci.vehicle.addLegacy(vehicleId, connection.routeId, lane=connection.fromLane,
                                        speed=5.0, typeID="CarA")
                self.vehiclesCount += 1

    def run(self):
        self.running = True
        try:
            while traci.simulation.getMinExpectedNumber() > 0:
                traci.simulationStep()
                # self.addVehicles()
        except:
            print("Connection was closed by SUMO")

        traci.close()
        sys.stdout.flush()
        self.running = False

    def performNonTrainingStep(self, selectedPhase):
        rewards = self.setSemaphore(selectedPhase)
        for step in range(Utils.SEMAPHORE_DECISION.value):
            self.addVehicles()
            traci.simulationStep()
            rewards += self.getReward()

        return rewards * 0.2

    def performStep(self, selectedPhase):
        rewards = self.setSemaphore(selectedPhase)

        for step in range(Utils.SEMAPHORE_DECISION.value):
            traci.simulationStep()
            rewards += self.getReward()
            # self.addVehicles()

        return rewards * 0.2

    def endConnection(self):
        traci.close()
        sys.stdout.flush()
        self.running = False

    def runForWarmUp(self, numberOfSteps):
        self.running = True
        try:
            while numberOfSteps > 0:
                traci.simulationStep()
                # self.addVehicles()
                numberOfSteps -= 1
            self.getVehiclesEntered(traci.simulation.getTime())
            self.getVehiclesLeft()
        except:
            print("Connection was closed by SUMO")
            traci.close()
            sys.stdout.flush()
            self.running = False
        self.currentSemaphorePhase = 6

    def changeLoadFactorForConnections(self, fromEdge, toEdge, newLoadFactor):
        for index in range(len(self.connections)):
            connection = self.connections[index]
            if connection.fromEdge is not fromEdge or connection.toEdge is not toEdge:
                continue
            connection.loadFactor = newLoadFactor
            self.connections[index] = connection

    def getReward(self, changed=False):
        reward = 0.0
        self.getVehiclesEntered(traci.simulation.getTime())
        vehiclesLeft = self.getVehiclesLeft()
        lanes = self.getLanes()
        reward += Utils.W1.value * self.getTotalQueueLength(lanes)
        reward += Utils.W2.value * self.getTotalDelay(lanes)
        reward += Utils.W3.value * self.getTotalWaitingTimesOfVehicles(lanes)
        reward += Utils.W4.value * (1.0 if changed else 0.0)
        reward += Utils.W5.value * len(vehiclesLeft)
        reward += Utils.W6.value * self.getTravelTimeDuration(vehiclesLeft)
        return reward

    def getLanes(self):
        lanes = set()
        for connection in self.connections:
            lanes.add(connection.getLaneId())
        return list(lanes)

    def getTotalQueueLength(self, lanes):
        queueLength = 0
        for lane in lanes:
            queueLength += traci.lane.getLastStepHaltingNumber(lane)
        return queueLength

    def getTotalDelay(self, lanes):
        totalDelay = 0.0
        for lane in lanes:
            totalDelay += 1.0 - (traci.lane.getLastStepMeanSpeed(lane) / traci.lane.getMaxSpeed(lane))

        return totalDelay

    def getTotalWaitingTimesOfVehicles(self, lanes):
        totalWaitingTime = 0
        for lane in lanes:
            totalWaitingTime += traci.lane.getWaitingTime(lane) / 60.0

        return totalWaitingTime

    def getTravelTimeDuration(self, vehiclesLeft):
        travelTimeDuration = 0
        currentTime = traci.simulation.getTime()
        for vehicle in vehiclesLeft:
            travelTimeDuration += (currentTime - self.enterTime[vehicle]) / 60.0

        return travelTimeDuration

    def getVehiclesLeft(self):
        vehicles_left = []
        vehicles = traci.vehicle.getIDList()
        for vehicle in vehicles:
            if not re.search(LANE_OUT_REGEX, traci.vehicle.getLaneID(vehicle)):
                if vehicle not in self.vehiclesLeft:
                    self.vehiclesLeft.add(vehicle)
                    vehicles_left.append(vehicle)

        return vehicles_left

    def getVehiclesEntered(self, currentTime):
        vehicles = traci.vehicle.getIDList()
        for vehicle in vehicles:
            if re.search(LANE_OUT_REGEX, traci.vehicle.getLaneID(vehicle)):
                if vehicle not in self.enterTime:
                    self.enterTime[vehicle] = currentTime
