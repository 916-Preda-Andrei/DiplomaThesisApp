import subprocess

from creators.ConnectionCreator import ConnectionCreator
from creators.EdgeCreator import EdgeCreator
from creators.RouteCreator import RouteCreator
from creators.TrafficLightsCreator import TrafficLightsCreator
from model.Edge import Edge


class NetworkCreator:
    BASH_COMMAND = "netconvert -c creators/sumo_files/app.netccfg"
    NR_OF_STREETS = 4

    def __init__(self, streets):
        self.connections = self.generateData(streets)

    def convertToMap(self, edges):
        edgesMap = {}
        for edge in edges:
            edgesMap[(edge.fromPoint, edge.toPoint)] = edge
        return edgesMap

    def generateData(self, streets):
        edges = []
        for street in streets.values():
            edges.append(Edge(street.streetType.value, 0, street.lanesOut))
            edges.append(Edge(0, street.streetType.value, street.lanesIn))
        # [Edge(1, 0, 6), Edge(0, 1, 2), Edge(2, 0, 4), Edge(0, 2, 3), Edge(3, 0, 4), Edge(0, 3, 2),
        #          Edge(4, 0, 4),
        #          Edge(0, 4, 5)]

        EdgeCreator(self.NR_OF_STREETS, edges)

        connectionCreator = ConnectionCreator(self.NR_OF_STREETS)
        edges.extend(self.generateFakeEdges(streets))
        connections = connectionCreator.createConnections(self.convertToMap(edges))
        connectionCreator.populate_file(connections)
        RouteCreator(self.NR_OF_STREETS, connections)
        TrafficLightsCreator(connections, streets)
        return connections

    def createNetworkFile(self):
        process = subprocess.Popen(self.BASH_COMMAND.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()

    def generateFakeEdges(self, streets):
        existingStreets = set([streetType.value for streetType in streets])
        fakeEdges = []
        for streetType in range(1, self.NR_OF_STREETS + 1):
            if streetType not in existingStreets:
                fakeEdges.append(Edge(streetType, 0, 0))
                fakeEdges.append(Edge(0, streetType, 0))
        return fakeEdges
