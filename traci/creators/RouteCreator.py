import random

from training.Utils import Utils


class RouteCreator:
    FILENAME = "creators/sumo_files/app.rou.xml"
    TAB = "   "

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
   <vType id="CarA" accel="0.8" decel="4.5" sigma="0.5" length="3" minGap="1" maxSpeed="16.67" guiShape="passenger"/>""",
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
            while counter < Utils.INITIAL_VEHICLE_COUNT.value:
                for connection in self.connections:
                    randomNumber = random.random()
                    if randomNumber < connection.loadFactor and counter < Utils.INITIAL_VEHICLE_COUNT.value:
                        print(self.TAB + "<vehicle depart=\"0\" id=\"I" + str(
                            counter) + "\" route=\"" + connection.routeId + "\" type=\"CarA\"/>", file=routesFile)
                        counter = counter + 1
