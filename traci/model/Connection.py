DEFAULT_LOAD_FACTOR = 0.05


class Connection:
    def __init__(self, fromEdge, toEdge, fromLane):
        self.fromEdge = fromEdge
        self.toEdge = toEdge
        self.fromLane = fromLane
        self.loadFactor = DEFAULT_LOAD_FACTOR
        self.laneId = "E_{}_0_{}".format(self.fromEdge, self.fromLane)
        self.routeId = "route_{}_{}".format(self.fromEdge, self.toEdge)
