import optparse
import os
import sys
from enum import Enum

from sumolib import checkBinary

from model.MoveType import MoveType


def checkSumoHome():
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:
        sys.exit("please declare environment variable 'SUMO_HOME'")


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")

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
    LOAD_REPLAY_BUFFER = False
    SAVE_TO_DRIVE = True
    EPISODES = 5000
    PRE_TRAINING_EPISODES = 500
    TOTAL_ITERATION_STEPS = 2000
    TOTAL_ITERATION_STEPS_PRE_TRAINING = 2000
    STARTING_STEP = 0
    LEARNING_STEPS = 15

    # Learning rate
    ALPHA = 0.0005

    # Gamma
    GAMMA_PRETRAIN = 0
    GAMMA = 0.8

    INPUT_DIMENSIONS = 38
    NUMBER_OF_ACTIONS = 4
    MEMORY_AFTER_UPDATE = 1000
    UPDATE_PERIOD = 300
    UPDATE_WITH_TARGET = 5
    MEMORY_SIZE = TOTAL_ITERATION_STEPS * UPDATE_WITH_TARGET + MEMORY_AFTER_UPDATE
    SAMPLE_SIZE = 600
    SAMPLE_SIZE_PRETRAIN = 3000
    BATCH_SIZE = 64

    MODEL_FILENAME = "dqn_model.h5"
    MEMORY_FILENAME = "replay_buffer.txt"

    PATH_TO_SUMOCFG_FILE = "creators/sumo_files/app.sumocfg"
    PATH_TO_SUMOCFG_FILE_TRAINING = "creators/sumo_files/cross_pretrain.sumocfg"
    PATH_TO_SUMOCFG_FILE_PRE_TRAINING = "creators/sumo_files/cross_pretrain.sumocfg"
    STEPS_UNTIL_FIRST_OBSERVATION = 30

    SEMAPHORE_DECISION = 5
    YELLOW_LIGHT = 3
    DEFAULT_SEMAPHORE_DURATION = 30

    MOVE_TYPES_IN_ORDER = [MoveType.NSR1, MoveType.WER2, MoveType.L1R1, MoveType.L2R2]

    # Weights for reward
    W1 = -0.4
    W2 = -0.25
    W3 = -0.4
    W4 = -5.0
    W5 = 1.0
    W6 = 1.0
    W7 = 1.0

    # Vehicle
    VEHICLE_SPEED = 5.0
