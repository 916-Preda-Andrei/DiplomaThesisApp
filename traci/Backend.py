from flask import Flask, request, jsonify

from controllers.App import App
from model.Load import Load
from model.Street import Street
from model.StreetType import StreetType

app = Flask(__name__)
service = App()


@app.after_request
def add_headers(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:4200'
    response.headers['Access-Control-Allow-Headers'] = "*"
    response.headers['Access-Control-Allow-Methods'] = "POST, GET, PUT, DELETE, OPTION"
    return response


@app.route('/start', methods=['GET'])
def start():
    if request.method == "GET":
        response, status = service.start()
        return jsonify({'message': response, 'status': status})


@app.route('/startOptimized', methods=['GET'])
def startOptimized():
    if request.method == "GET":
        response, status = service.startOptimized()
        return jsonify({'message': response, 'status': status})


def computeStreetType(street):
    if street == "west":
        return StreetType.WEST
    if street == "east":
        return StreetType.EAST
    if street == "south":
        return StreetType.SOUTH
    if street == "north":
        return StreetType.NORTH
    return None


@app.route('/edit/streets', methods=['POST'])
def editStreets():
    if request.method != "POST":
        return "Bad Request", 400

    jsonStreets = request.json
    streets = []
    for streetObject in jsonStreets:
        street = streetObject['street']
        lanesIn = int(streetObject['lanesIn'])
        lanesOut = int(streetObject['lanesOut'])
        if street is None or lanesIn is None or lanesOut is None:
            return "A street must have non-empty values for parameters: street, lanesIn and lanesOut", 400
        streets.append(Street(computeStreetType(street), lanesIn, lanesOut))

    response, status = service.editStreets(streets)
    return jsonify({'message': response, 'status': status})


@app.route('/edit/loads', methods=['POST'])
def editLoads():
    if request.method != "POST":
        return "Bad Request", 400
    jsonLoads = request.json
    loads = []
    for loadObject in jsonLoads:
        fromEdge = loadObject['from']
        toEdge = loadObject['to']
        loadFactor = loadObject['loadFactor']
        loads.append(Load(computeStreetType(fromEdge), computeStreetType(toEdge), loadFactor))

    response, status = service.editLoads(loads)
    return jsonify({'message': response, 'status': status})


if __name__ == '__main__':
    app.run(debug=False)
