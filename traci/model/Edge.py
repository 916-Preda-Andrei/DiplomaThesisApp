class Edge:
    def __init__(self, fromPoint, toPoint, lanes):
        self.fromPoint = fromPoint
        self.toPoint = toPoint
        self.lanes = lanes

    def computeId(self):
        return "E_" + str(self.fromPoint) + "_" + str(self.toPoint)
