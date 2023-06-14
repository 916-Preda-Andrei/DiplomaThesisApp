from __future__ import absolute_import
from __future__ import print_function

from threading import Thread

from controllers.Runner import Runner
from creators.NetworkCreator import NetworkCreator
from optimization.Agent import Agent
from controllers.Environment import Environment
from Utils import Utils


class Service:
    def __init__(self):
        self.networkCreator = None
        self.runner = None
        self.semaphoreDuration = None

    def createNetwork(self):
        self.networkCreator = NetworkCreator(self.semaphoreDuration)
        self.networkCreator.createNetworkFile()

    def start(self, mode):
        if self.runner is not None and self.runner.running:
            return "SUMO already started", 405

        if self.networkCreator is None:
            self.createNetwork()
        self.runner = Runner(self.networkCreator.connections)

        if mode == "normal":
            self.runner.startSimulator(Utils.PATH_TO_SUMOCFG_FILE.value)
        else:
            self.runner.startSimulator(Utils.PATH_TO_SUMOCFG_FILE_PRE_TRAINING.value)

        thread = Thread(target=self.runner.run, args=(mode,))
        thread.start()

        return "Successfully started SUMO Simulator", 200

    def startOptimized(self, mode):
        if self.runner is not None and self.runner.running:
            return "SUMO already started", 405

        self.createNetwork()
        self.runner = Runner(self.networkCreator.connections)
        env = Environment()
        agent = Agent(alpha=Utils.ALPHA.value, numberOfActions=Utils.NUMBER_OF_ACTIONS.value,
                      batchSize=Utils.BATCH_SIZE.value,
                      inputDimensions=Utils.INPUT_DIMENSIONS.value, memorySize=Utils.MEMORY_SIZE.value,
                      filename=Utils.MODEL_FILENAME.value, memoryFilename=Utils.MEMORY_FILENAME.value,
                      learningStepsToTake=Utils.LEARNING_STEPS.value)
        agent.loadModel()
        if mode == "normal":
            env.createFrom(self.networkCreator, self.runner)
            self.runner.startSimulator(Utils.PATH_TO_SUMOCFG_FILE.value)

        thread = Thread(target=self.runOptimized, args=(env, agent, mode))
        thread.start()

        return "Successfully started SUMO Simulator", 200

    def runOptimized(self, env, agent, mode):
        if mode == "training":
            observation = env.reset(preTraining=True)
        else:
            observation = env.warmUp()
        try:
            done = False
            while not done:
                action = agent.chooseBestAction(observation)
                if mode == "training":
                    newObservation, reward, done = env.step(action)
                else:
                    newObservation, reward = env.nonTrainingStep(action)
                observation = newObservation
        except:
            print("Connection was closed by SUMO")
        finally:
            self.runner.endConnection()

    def editLoads(self, loads):
        for connection in self.networkCreator.connections:
            for load in loads:
                if load.fromEdge.value == connection.fromEdge and load.toEdge.value == connection.toEdge:
                    connection.loadFactor = load.loadFactor * 0.01
                    break

        if self.runner is not None:
            self.runner.connections = self.networkCreator.connections
        return "Successfully edited the connections", 200

    def editSemaphores(self, semaphores):
        if self.runner is not None and self.runner.running:
            return "SUMO is started. Cannot edit semaphore program now.", 405

        self.semaphoreDuration = semaphores
        self.createNetwork()
        return "Semaphores edited successfully.", 200
