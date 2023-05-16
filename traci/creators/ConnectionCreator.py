from exceptions.TrafficAppException import TrafficAppException
from model.Connection import Connection


class ConnectionCreator:
    FILENAME = "creators/sumo_files/app.con.xml"
    TAB = "   "
    oppositeStreets = {1: 2, 2: 1, 3: 4, 4: 3}
    leftStreets = {1: 4, 2: 3, 3: 1, 4: 2}
    rightStreets = {1: 3, 2: 4, 3: 2, 4: 1}

    def __init__(self, nr_of_streets):
        self.nr_of_streets = nr_of_streets
        self.init_file()

    def init_file(self):
        with open(self.FILENAME, "w") as connections_file:
            print("""<?xml version="1.0" encoding="iso-8859-1"?>
<connections xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/connections_file.xsd">""",
                  file=connections_file)

    def end_file(self):
        with open(self.FILENAME, "a") as connections_file:
            print("</connections>", file=connections_file)

    def populate_file(self, connections):
        with open(self.FILENAME, "a") as connections_file:
            for connection in connections:
                fromEdge = str(connection.fromEdge)
                toEdge = str(connection.toEdge)
                fromLane = str(connection.fromLane)
                toLane = str(connection.toLane)

                print(
                    self.TAB + "<connection from=\"" + fromEdge + "\" to=\"" + toEdge + "\" fromLane=\"" + fromLane + "\" toLane=\"" + toLane + "\"/>",
                    file=connections_file)

        self.end_file()

    def createConnections(self, edges):
        connections = []
        for streetNumber in range(1, self.nr_of_streets + 1):
            street = edges.get((streetNumber, 0))
            if street is None or street.lanes == 0:
                continue

            leftStreet = edges.get((0, self.leftStreets.get(streetNumber)))
            frontStreet = edges.get((0, self.oppositeStreets.get(streetNumber)))
            rightStreet = edges.get((0, self.rightStreets.get(streetNumber)))

            totalOptions = leftStreet.lanes
            totalOptions += frontStreet.lanes
            totalOptions += rightStreet.lanes
            if totalOptions < street.lanes:
                raise TrafficAppException("Not enough lanes!")

            if street.lanes == 1:
                connections.extend(self.createConnectionForStreetWithOneLane(street, leftStreet, frontStreet, rightStreet))
            elif street.lanes == 2:
                connections.extend(self.createConnectionForStreetWithTwoLanes(street, leftStreet, frontStreet, rightStreet))
            else:
                connections.extend(self.createConnectionForStreet(street, leftStreet, frontStreet, rightStreet))

        return connections

    def createConnectionForStreet(self, street, leftStreet, frontStreet, rightStreet):
        availableLanes = street.lanes

        leftLanes = leftStreet.lanes
        frontLanes = frontStreet.lanes
        rightLanes = rightStreet.lanes
        totalOptions = leftLanes + frontLanes + rightLanes

        connections = []
        streetId = street.computeId()
        leftStreetId = leftStreet.computeId()
        frontStreetId = frontStreet.computeId()
        rightStreetId = rightStreet.computeId()

        takeLeftLanes = 0
        takeFrontLanes = min(1, frontLanes)
        takeRightLanes = 0
        if availableLanes - takeFrontLanes > 0:
            takeRightLanes = min(1, rightLanes)
        if availableLanes - takeFrontLanes - takeRightLanes > 0:
            takeLeftLanes = min(1, leftLanes)

        takeLeftLanes = min(max(takeLeftLanes, min(int((leftLanes / totalOptions) * availableLanes), availableLanes - takeRightLanes - takeFrontLanes)), leftLanes)
        totalOptions -= leftLanes
        availableLanes -= takeLeftLanes

        takeRightLanes = min(max(1, min(int((rightLanes / totalOptions) * availableLanes), availableLanes - takeFrontLanes)), rightLanes)
        availableLanes -= takeRightLanes
        takeFrontLanes = availableLanes

        if takeRightLanes > 0:
            for laneTo in range(rightLanes):
                laneFrom = int((takeRightLanes / rightLanes) * laneTo)
                connections.append(Connection(streetId, rightStreetId, laneFrom, laneTo))
        if takeFrontLanes > 0:
            for laneTo in range(frontLanes):
                laneFrom = takeRightLanes + int((takeFrontLanes / frontLanes) * laneTo)
                connections.append(Connection(streetId, frontStreetId, laneFrom, laneTo))
        if takeLeftLanes > 0:
            for laneTo in range(leftLanes):
                laneFrom = takeRightLanes + takeFrontLanes + int((takeLeftLanes / leftLanes) * laneTo)
                connections.append(Connection(streetId, leftStreetId, laneFrom, laneTo))

        return connections

    def createConnectionForStreetWithOneLane(self, street, leftStreet, frontStreet, rightStreet):
        connections = []
        if frontStreet.lanes > 0:
            for i in range(frontStreet.lanes):
                connections.append(Connection(street.computeId(), frontStreet.computeId(), 0, i))
        elif rightStreet.lanes > 0:
            for i in range(rightStreet.lanes):
                connections.append(Connection(street.computeId(), rightStreet.computeId(), 0, i))
        elif leftStreet.lanes > 0:
            for i in range(leftStreet.lanes):
                connections.append(Connection(street.computeId(), leftStreet.computeId(), 0, i))

        return connections

    def createConnectionForStreetWithTwoLanes(self, street, leftStreet, frontStreet, rightStreet):
        connections = []

        if rightStreet.lanes > 0 and frontStreet.lanes > 0:
            for i in range(rightStreet.lanes):
                connections.append(Connection(street.computeId(), rightStreet.computeId(), 0, i))
            for i in range(frontStreet.lanes):
                connections.append(Connection(street.computeId(), frontStreet.computeId(), 1, i))

        elif rightStreet.lanes > 0 and leftStreet.lanes > 0:
            for i in range(rightStreet.lanes):
                connections.append(Connection(street.computeId(), rightStreet.computeId(), 0, i))
            for i in range(leftStreet.lanes):
                connections.append(Connection(street.computeId(), leftStreet.computeId(), 1, i))

        elif leftStreet.lanes > 0 and frontStreet.lanes > 0:
            for i in range(leftStreet.lanes):
                connections.append(Connection(street.computeId(), leftStreet.computeId(), 1, i))
            for i in range(frontStreet.lanes):
                connections.append(Connection(street.computeId(), frontStreet.computeId(), 0, i))

        else:
            connections = self.createConnectionForStreet(street, leftStreet, frontStreet,rightStreet)

        return connections