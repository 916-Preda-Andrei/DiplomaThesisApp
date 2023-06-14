import subprocess

from creators.TrafficLightsCreator import TrafficLightsCreator
from model.Connection import Connection
from Utils import Utils


class NetworkCreator:
    BASH_COMMAND = "netconvert -c creators/sumo_files/app.netccfg"
    NR_OF_STREETS = 4

    def __init__(self, semaphoreDuration=None):
        self.semaphoreDuration = semaphoreDuration
        if semaphoreDuration is None:
            self.semaphoreDuration = self.createDefaultSemaphore()

        self.connections = self.generateData()

    def generateData(self):
        connections = self.createConnections()
        TrafficLightsCreator(self.semaphoreDuration)
        return connections

    def createConnections(self):
        return [
            Connection(1, 2, 1), Connection(1, 3, 0), Connection(1, 4, 2),
            Connection(2, 1, 1), Connection(2, 3, 2), Connection(2, 4, 0),
            Connection(3, 1, 2), Connection(3, 2, 0), Connection(3, 4, 1),
            Connection(4, 1, 0), Connection(4, 2, 2), Connection(4, 3, 1)
        ]

    def createNetworkFile(self):
        process = subprocess.Popen(self.BASH_COMMAND.split(), stdout=subprocess.PIPE)
        process.communicate()

    def createDefaultSemaphore(self):
        durations = {}
        for moveType in Utils.MOVE_TYPES_IN_ORDER.value:
            durations[moveType] = Utils.DEFAULT_SEMAPHORE_DURATION.value
        return durations
