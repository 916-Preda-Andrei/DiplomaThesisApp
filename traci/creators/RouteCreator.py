import random


class RouteCreator:
    FILENAME = "creators/sumo_files/app.rou.xml"
    TAB = "   "
    INITIAL_VEHICLE_COUNT = 20

    def __init__(self, nr_of_streets, connections):
        self.nr_of_streets = nr_of_streets
        self.connections = connections
        self.init_file()
        self.populate_file()
        self.end_file()

    def init_file(self):
        with open(self.FILENAME, "w") as routesFile:
            print("""<?xml version="1.0" encoding="UTF-8"?>
<routes>
   <vType accel="3.0" decel="6.0" id="CarA" length="5.0" minGap="0" maxSpeed="20.0" sigma="0.5" />""",
                  file=routesFile)

    def end_file(self):
        with open(self.FILENAME, "a") as routesFile:
            print("</routes>", file=routesFile)

    def populate_file(self):
        with open(self.FILENAME, "a") as routesFile:
            appeared = {}
            for connection in self.connections:
                fromEdge = connection.fromEdge
                toEdge = connection.toEdge
                if (fromEdge, toEdge) in appeared:
                    connection.routeId = appeared.get((fromEdge, toEdge))
                    continue

                routeId = "route" + str(len(appeared) + 1)
                appeared[(fromEdge, toEdge)] = routeId
                connection.routeId = routeId

                edges = str(fromEdge) + " " + str(toEdge)
                print(self.TAB + "<route id=\"" + routeId + "\" edges=\"" + edges + "\"/>", file=routesFile)
        self.addInitialVehicles()

    def addInitialVehicles(self):
        counter = 0
        with open(self.FILENAME, "a") as routesFile:
            while counter < self.INITIAL_VEHICLE_COUNT:
                for connection in self.connections:
                    randomNumber = random.random()
                    if randomNumber < connection.loadFactor and counter < self.INITIAL_VEHICLE_COUNT:
                        print(self.TAB + "<vehicle depart=\"0\" id=\"I" + str(counter) + "\" route=\"" + connection.routeId + "\" type=\"CarA\"/>", file=routesFile)
                        counter = counter + 1
