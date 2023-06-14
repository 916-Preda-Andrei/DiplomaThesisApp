from flask import Flask, request, jsonify

from controllers.Service import Service
from model.Load import Load
from model.MoveType import MoveType
from model.StreetType import StreetType

app = Flask(__name__)
service = Service()


@app.after_request
def add_headers(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:4200'
    response.headers['Access-Control-Allow-Headers'] = "*"
    response.headers['Access-Control-Allow-Methods'] = "POST, GET, PUT, DELETE"
    return response


@app.route('/start/<mode>', methods=['GET'])
def start(mode):
    if request.method == "GET":
        response, status = service.start(mode)
        return jsonify({'message': response, 'status': status})


@app.route('/startOptimized/<mode>', methods=['GET'])
def startOptimized(mode):
    if request.method == "GET":
        response, status = service.startOptimized(mode)
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


def computeMoveType(moveType):
    if moveType == "NSR1":
        return MoveType.NSR1
    if moveType == "WER2":
        return MoveType.WER2
    if moveType == "L1R1":
        return MoveType.L1R1
    if moveType == "L2R2":
        return MoveType.L2R2
    return None

@app.route('/edit/semaphores', methods=['POST'])
def editSemaphores():
    if request.method != "POST":
        return "Bad Request", 400
    jsonSemaphores = request.json
    semaphores = {}
    for semaphoreObject in jsonSemaphores:
        moveType = computeMoveType(semaphoreObject['moveType'])
        duration = int(semaphoreObject['duration'])
        semaphores[moveType] = duration

    response, status = service.editSemaphores(semaphores)
    return jsonify({'message': response, 'status': status})

if __name__ == '__main__':
    app.run(debug=False)
