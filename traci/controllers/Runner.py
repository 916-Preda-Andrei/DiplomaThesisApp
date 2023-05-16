import random
import sys

import traci

from model.MoveType import MoveType
from training.Utils import Utils

vehiclesCount = 0

initialSemaphorePhases = [MoveType.NSR1, MoveType.WER2, MoveType.L1R1, MoveType.L2R2]

class Runner:
    def __init__(self, connections):
        self.connections = connections
        self.running = False
        self.currentSemaphorePhase = 0

    def setSemaphore(self, selectedPhase):
        if selectedPhase != self.currentSemaphorePhase:
            self.currentSemaphorePhase += 1
            traci.trafficlight.setPhase("0", str(self.currentSemaphorePhase))

            for i in range(Utils.YELLOW_LIGHT.value):
                traci.simulationStep()
                self.addVehicles()

            self.currentSemaphorePhase = selectedPhase
            traci.trafficlight.setPhase("0", str(self.currentSemaphorePhase))

    def addVehicles(self):
        global vehiclesCount
        for connection in self.connections:
            randomNumber = random.random()
            if randomNumber < connection.loadFactor:
                traci.vehicle.addLegacy("V" + str(vehiclesCount), connection.routeId, lane=connection.fromLane, speed=10, typeID="CarA")
                vehiclesCount = vehiclesCount + 1
                # print("Added vehicle")

    def run(self):
        self.running = True
        try:
            while traci.simulation.getMinExpectedNumber() > 0:
                traci.simulationStep()
                self.addVehicles()
        except:
            print("Connection was closed by SUMO")

        traci.close()
        sys.stdout.flush()
        self.running = False

    # def runOptimized(self):
    #     self.running = True
    #     step = 0
    #     try:
    #         while traci.simulation.getMinExpectedNumber() > 0:
    #             if step == Utils.SEMAPHORE_DECISION.value:
    #                 #TODO: Take decision based on state
    #                 pass
    #
    #             traci.simulationStep()
    #             self.addVehicles()
    #             step += 1
    #     except:
    #         print("Connection was closed by SUMO")
    #
    #     traci.close()
    #     sys.stdout.flush()
    #     self.running = False

    def performStep(self, selectedPhase):
        initialWaitingTime = self.getTotalWaitingTimesOfVehicles()
        self.setSemaphore(selectedPhase)
        
        for step in range(Utils.SEMAPHORE_DECISION.value):
            traci.simulationStep()
            self.addVehicles()
            
        afterActionWaitingTime = self.getTotalWaitingTimesOfVehicles()
        return initialWaitingTime - afterActionWaitingTime

    def endConnection(self):
        traci.close()
        sys.stdout.flush()
        self.running = False

    def runForWarmUp(self, numberOfSteps):
        self.running = True
        try:
            while numberOfSteps > 0:
                traci.simulationStep()
                self.addVehicles()
                numberOfSteps -= 1
        except:
            print("Connection was closed by SUMO")
            traci.close()
            sys.stdout.flush()
            self.running = False

    def changeLoadFactorForConnections(self, fromEdge, toEdge, newLoadFactor):
        for index in range(len(self.connections)):
            connection = self.connections[index]
            if connection.fromEdge is not fromEdge or connection.toEdge is not toEdge:
                continue
            connection.loadFactor = newLoadFactor
            self.connections[index] = connection

    def getTotalWaitingTimesOfVehicles(self):
        totalWaitingTime = 0
        vehicles = traci.vehicle.getIDList()
        for vehicle in vehicles:
            if traci.vehicle.getSpeed(vehicle) > 1.0:
                totalWaitingTime += traci.vehicle.getAccumulatedWaitingTime(vehicle)

        return totalWaitingTime
