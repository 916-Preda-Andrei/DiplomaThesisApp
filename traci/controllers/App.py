from __future__ import absolute_import
from __future__ import print_function

from threading import Thread

import traci

from controllers.Runner import Runner
from creators.NetworkCreator import NetworkCreator
from exceptions.TrafficAppException import TrafficAppException
from training.Agent import Agent
from training.Environment import Environment
from training.Utils import Utils, getSumoBinary


class App:
    def __init__(self):
        self.networkCreator = None
        self.runner = None
        self.streets = {}

    def createNetwork(self):
        self.networkCreator = NetworkCreator(self.streets)
        self.networkCreator.createNetworkFile()

    def start(self):
        if self.runner is not None and self.runner.running:
            return "SUMO already started", 405

        if self.networkCreator is None:
            return "No network has been created yet", 404

        self.runner = Runner(self.networkCreator.connections)

        sumoBinary = getSumoBinary()
        traci.start([sumoBinary, "-c", Utils.PATH_TO_SUMOCFG_FILE.value,
                     "--tripinfo-output", "app.tripinfo.xml"])
        thread = Thread(target=self.runner.run)
        thread.start()

        return "Successfully started SUMO Simulator", 200

    def startOptimized(self):
        if self.runner is not None and self.runner.running:
            return "SUMO already started", 405

        if self.networkCreator is None:
            return "No network has been created yet", 404

        self.runner = Runner(self.networkCreator.connections)
        env = Environment()
        agent = Agent(alpha=Utils.ALPHA.value, gamma=Utils.GAMMA.value, numberOfActions=Utils.NUMBER_OF_ACTIONS.value,
                      batchSize=Utils.BATCH_SIZE.value,
                      inputDimensions=Utils.INPUT_DIMENSIONS.value, memorySize=Utils.MEMORY_SIZE.value,
                      filename=Utils.MODEL_FILENAME.value, memoryFilename=Utils.MEMORY_FILENAME.value,
                      learningStepsToTake=Utils.LEARNING_STEPS.value)
        agent.loadModel()
        env.createFrom(self.networkCreator, self.runner, self.streets)

        sumoBinary = getSumoBinary()
        traci.start([sumoBinary, "-c", Utils.PATH_TO_SUMOCFG_FILE.value,
                     "--tripinfo-output", "app.tripinfo.xml"])
        thread = Thread(target=self.runOptimized, args=(env, agent))
        thread.start()

        return "Successfully started SUMO Simulator", 200

    def runOptimized(self, env, agent):
        observation = env.warmUp()
        try:
            while traci.simulation.getMinExpectedNumber() > 0:
                action = agent.chooseBestAction(observation)
                newObservation, reward = env.nonTrainingStep(action)
                observation = newObservation
        except:
            print("Connection was closed by SUMO")
        finally:
            self.runner.endConnection()

    def setStreets(self, streets):
        if self.runner is not None and self.runner.running:
            raise TrafficAppException("SUMO is running. No modifications can be made!")

        for street in streets:
            self.streets[street.streetType] = street

        self.createNetwork()

    def editStreets(self, streets):
        if self.runner is not None and self.runner.running:
            return "SUMO is running. No modifications can be made!", 200

        for street in streets:
            self.streets[street.streetType] = street

        self.createNetwork()

        return "Successfully edited the streets", 200

    def editLoads(self, loads):
        for connection in self.networkCreator.connections:
            for load in loads:
                if load.fromEdge.value == connection.getFromEdge() and load.toEdge.value == connection.getToEdge():
                    connection.loadFactor = load.loadFactor * 0.01
                    break

        if self.runner is not None:
            self.runner.connections = self.networkCreator.connections
        return "Successfully edited the connections", 200
