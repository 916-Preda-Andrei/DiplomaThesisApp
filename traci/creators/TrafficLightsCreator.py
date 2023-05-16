from model.MoveType import MoveType
from model.StreetType import StreetType
from training.Utils import directionMapper, Utils


class TrafficLightsCreator:
    FILENAME = "creators/sumo_files/app.program.xml"
    TAB = "   "

    def __init__(self, connections, streets):
        self.STREET_TYPES_CLOCKWISE = [StreetType.NORTH, StreetType.EAST, StreetType.SOUTH, StreetType.WEST]
        self.connections = connections
        self.streets = streets
        self.init_file()
        self.populate_file()
        self.end_file()

    def init_file(self):
        with open(self.FILENAME, "w") as program_file:
            print("""<additional>
    <tlLogic id ="0" programID="trafficLightsProgram" offset="0" type="static">""",
                  file=program_file)

    def end_file(self):
        with open(self.FILENAME, "a") as program_file:
            print("""    </tlLogic>
</additional>""", file=program_file)

    def populate_file(self):
        connectionsForLane = {}
        toStreetForLane = {}
        indexesOfMoveType = {MoveType.NSR1: [], MoveType.WER2: [], MoveType.L1R1: [], MoveType.L2R2: []}

        for connection in self.connections:
            if (int(connection.fromEdge[2]), connection.fromLane) not in connectionsForLane:
                connectionsForLane[(int(connection.fromEdge[2]), connection.fromLane)] = 0
                toStreetForLane[(int(connection.fromEdge[2]), connection.fromLane)] = int(connection.toEdge[4])
            connectionsForLane[(int(connection.fromEdge[2]), connection.fromLane)] += 1

        currentIndex = 0
        for streetType in self.STREET_TYPES_CLOCKWISE:
            for lane in range(self.streets[streetType].lanesOut):
                moveTypes = directionMapper[(streetType.value, toStreetForLane[(streetType.value, lane)])]
                for i in range(connectionsForLane[(streetType.value, lane)]):
                    for moveType in moveTypes:
                        indexesOfMoveType[moveType].append(currentIndex)
                    currentIndex += 1

        phases = []
        for moveType in indexesOfMoveType.keys():
            currentState = ["r" for _ in range(currentIndex)]
            yellowState = ["r" for _ in range(currentIndex)]
            for index in indexesOfMoveType[moveType]:
                currentState[index] = "G"
                yellowState[index] = "y"
            phases.append(''.join(s for s in currentState))
            phases.append(''.join(s for s in yellowState))

        with open(self.FILENAME, "a") as program_file:
            yellow = False
            for phase in phases:
                if yellow:
                    print(self.TAB * 2 + "<phase duration=\"" + str(
                        Utils.YELLOW_LIGHT.value) + "\" state=\"" + phase + "\"/>", file=program_file)
                else:
                    print(self.TAB * 2 + "<phase duration=\"" + str(
                        Utils.DEFAULT_SEMAPHORE_DURATION.value) + "\" state=\"" + phase + "\"/>", file=program_file)
                yellow = not yellow
