import optparse
import os
import sys
from enum import Enum

from sumolib import checkBinary

from model.MoveType import MoveType
from model.StreetType import StreetType

directionMapper = {(1, 2): [MoveType.WER2], (1, 3): [MoveType.WER2, MoveType.L2R2], (1, 4): [MoveType.L1R1],
                   (2, 1): [MoveType.WER2],
                   (2, 3): [MoveType.L1R1], (2, 4): [MoveType.WER2, MoveType.L2R2], (3, 1): [MoveType.L2R2],
                   (3, 2): [MoveType.L1R1, MoveType.NSR1],
                   (3, 4): [MoveType.NSR1], (4, 1): [MoveType.NSR1, MoveType.L1R1], (4, 2): [MoveType.L2R2],
                   (4, 3): [MoveType.NSR1]}

allMoveTypes = [MoveType.NSR1, MoveType.WER2, MoveType.L1R1, MoveType.L2R2]
allStreetTypes = [StreetType.WEST, StreetType.EAST, StreetType.SOUTH, StreetType.NORTH]


def checkSumoHome():
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:
        sys.exit("please declare environment variable 'SUMO_HOME'")


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=True, help="run the commandline version of sumo")

    options, args = optParser.parse_args()
    return options


def getSumoBinary():
    checkSumoHome()
    options = get_options()
    if options.nogui:
        return checkBinary('sumo')
    return checkBinary('sumo-gui')


class Utils(Enum):
    LOAD_MODEL = False
    LOAD_REPLAY_BUFFER = True
    SAVE_TO_DRIVE = True
    STARTING_EPISODE = 0
    EPISODES = 200
    TOTAL_ITERATION_STEPS = 1000
    LEARNING_STEPS = 800
    GAMMA = 0.75

    # Learning rate
    ALPHA = 0.0005

    INPUT_DIMENSIONS = 8
    NUMBER_OF_ACTIONS = 4
    MEMORY_SIZE = 50000
    BATCH_SIZE = 100

    MODEL_FILENAME = "dqn_model.h5"
    MEMORY_FILENAME = "replay_buffer.txt"
    MODEL_PNG = "training.png"

    PATH_TO_SUMOCFG_FILE = "creators/sumo_files/app.sumocfg"
    STEPS_UNTIL_FIRST_OBSERVATION = 129  # 4 * 30 + 3 * 3

    SEMAPHORE_DECISION = 5
    YELLOW_LIGHT = 3
    DEFAULT_SEMAPHORE_DURATION = 30

    initialSemaphorePhases = [MoveType.NSR1, MoveType.WER2, MoveType.L1R1, MoveType.L2R2]
