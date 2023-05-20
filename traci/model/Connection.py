DEFAULT_LOAD_FACTOR = 0.05

class Connection:
    def __init__(self, fromEdge, toEdge, fromLane, toLane):
        self.fromEdge = fromEdge
        self.toEdge = toEdge
        self.fromLane = fromLane
        self.toLane = toLane
        self.loadFactor = DEFAULT_LOAD_FACTOR
        self.routeId = None

    def getLaneId(self):
        return "E_{}_0_{}".format(self.getFromEdge(), self.fromLane)

    def getFromEdge(self):
        return int(self.fromEdge[2])

    def getToEdge(self):
        return int(self.toEdge[4])