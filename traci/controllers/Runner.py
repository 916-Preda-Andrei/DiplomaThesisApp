import random
import re
import sys

import traci

from Utils import Utils, getSumoBinary

LANE_OUT_REGEX = "^E_[1234]_0_[012345]$"


class Runner:
    def __init__(self, connections):
        self.connections = connections
        self.lanes = self.getLanes()
        self.running = False
        self.currentSemaphorePhase = 0
        self.vehiclesCount = 0
        self.vehiclesLeft = set()
        self.freshChanged = False
        self.enterTime = {}

    def startSimulator(self, sumoFile):
        sumoBinary = getSumoBinary()
        traci.start([sumoBinary, "-c", sumoFile, "--start", "--quit-on-end", "--waiting-time-memory", "10000"])


    def setSemaphore(self, selectedPhase):
        rewards = 0.0
        if selectedPhase != self.currentSemaphorePhase:
            wasFreshChange = self.freshChanged
            changed = True

            self.freshChanged = True
            self.currentSemaphorePhase += 1
            traci.trafficlight.setPhase("0", str(self.currentSemaphorePhase))

            for i in range(Utils.YELLOW_LIGHT.value):
                traci.simulationStep()
                rewards += self.getReward(changed, wasFreshChange)
                wasFreshChange = False
                changed = False

            self.currentSemaphorePhase = selectedPhase
        else:
            self.freshChanged = False

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

    def run(self, mode):
        self.running = True
        try:
            while traci.simulation.getMinExpectedNumber() > 0:
                if mode == "normal":
                    self.addVehicles()
                traci.simulationStep()
        except:
            print("Connection was closed by SUMO")
        self.endConnection()

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
                numberOfSteps -= 1
            self.getVehiclesEntered(traci.simulation.getTime())
            self.getVehiclesLeft()
        except:
            print("Connection was closed by SUMO")
            traci.close()
            sys.stdout.flush()
            self.running = False
        self.currentSemaphorePhase = 0

    def getReward(self, changed=False, wasFreshChange=False):
        reward = 0.0
        self.getVehiclesEntered(traci.simulation.getTime())
        vehiclesLeft = self.getVehiclesLeft()
        lanes = self.lanes
        reward += Utils.W1.value * self.getTotalQueueLength(lanes)
        reward += Utils.W2.value * self.getTotalDelay(lanes)
        reward += Utils.W3.value * self.getTotalWaitingTimesOfVehicles(lanes)
        reward += Utils.W4.value * (1.0 if changed else 0.0)
        reward += Utils.W5.value * len(vehiclesLeft)
        reward += Utils.W6.value * self.getTravelTimeDuration(vehiclesLeft)
        reward += Utils.W7.value * (1.0 if wasFreshChange else 0.0)
        return reward

    def getLanes(self):
        lanes = set()
        for connection in self.connections:
            lanes.add(connection.laneId)
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

    def collectCountDataForLane(self, lane):
        return traci.lane.getLastStepVehicleNumber(lane)

    def collectWaitingDataForLane(self, lane):
        return traci.lane.getWaitingTime(lane) / 60.0

    def collectQueueDataForLane(self, lane):
        return traci.lane.getLastStepHaltingNumber(lane)
