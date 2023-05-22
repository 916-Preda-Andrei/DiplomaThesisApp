import json
from json import JSONEncoder

import numpy as np
import ast

from model.MoveType import MoveType
from training.Utils import Utils
from training.ReplayBuffer import ReplayBuffer
from keras.layers import Dense, Activation
from keras.models import Sequential, load_model
from keras.optimizers import Adam


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


def buildDQN(learningRate, numberOfActions, inputDimensions, firstFullyConnectedLayerDimensions,
             secondFullyConnectedLayerDimensions):
    model = Sequential([
        Dense(firstFullyConnectedLayerDimensions, input_shape=(inputDimensions,)),
        Activation('relu'),
        Dense(secondFullyConnectedLayerDimensions),
        Activation('relu'),
        Dense(numberOfActions, activation='linear'),
    ])

    model.compile(optimizer=Adam(lr=learningRate), loss='mse')
    return model


class Agent(object):
    def __init__(self, alpha, gamma, numberOfActions, batchSize, inputDimensions, memorySize, filename, memoryFilename,
                 learningStepsToTake):
        self.actionSpace = [move.value for move in MoveType]
        self.numberOfActions = numberOfActions
        self.gamma = gamma
        self.epsilon = 0.0
        self.batchSize = batchSize
        self.modelFile = filename
        self.memoryFile = memoryFilename
        self.memory = ReplayBuffer(memorySize, inputDimensions, numberOfActions, discrete=True)
        self.qEval = buildDQN(alpha, numberOfActions, inputDimensions, 256, 256)
        self.learningStepsToTake = learningStepsToTake

    def remember(self, state, action, reward, newState):
        self.memory.storeTransition(state, action, reward, newState)

    def chooseAction(self, state):
        rand = np.random.random()
        if rand < self.epsilon:
            action = np.random.choice(self.actionSpace)
        else:
            actions = self.qEval.predict([state], verbose=None)
            action = np.argmax(actions)
        return action

    def chooseBestAction(self, state):
        actions = self.qEval.predict([state])
        return np.argmax(actions)

    def learn(self):
        if self.memory.memoryCounter < self.batchSize:
            return

        for _ in range(self.learningStepsToTake):
            states, actions, rewards, newStates = self.memory.sampleBuffer(self.batchSize)

            # actionValues = np.array(self.actionSpace, dtype=np.int8)
            # actionIndices = np.dot(actions, actionValues)

            qEval = self.qEval.predict([states], verbose=None)
            qNext = self.qEval.predict([newStates], verbose=None)

            x = np.zeros((self.batchSize, Utils.INPUT_DIMENSIONS.value))
            y = np.zeros((self.batchSize, Utils.NUMBER_OF_ACTIONS.value))

            for i in range(self.batchSize):
                state, action, reward = states[i], actions[i], rewards[i]
                currentQ = qEval[i]
                currentQ[action] = reward + self.gamma * np.amax(qNext[i])
                x[i] = state
                y[i] = currentQ
                # batchIndex = np.arange(self.batchSize, dtype=np.int32)
                #
                # self.qTarget[batchIndex, actionIndices] = rewards + self.gamma * np.max(qNext, axis=1)

            self.qEval.fit(x, y, epochs=1, verbose=0)

    def saveModel(self):
        self.qEval.save(self.modelFile)
        with open(self.memoryFile, "w") as memory:
            print(self.memory.memoryCounter, file=memory)
            for i in range(self.memory.memorySize):
                print(json.dumps(self.memory.stateMemory[i], cls=NumpyArrayEncoder), file=memory)
                print(json.dumps(self.memory.actionMemory[i], cls=NumpyArrayEncoder), file=memory)
                print(self.memory.rewardMemory[i], file=memory)
                print(json.dumps(self.memory.newStateMemory[i], cls=NumpyArrayEncoder), file=memory)

    def loadModel(self):
        self.qEval = load_model(self.modelFile)
        with open(self.memoryFile) as memory:
            line_nr = 0
            for line in memory:
                if line_nr == 0:
                    self.memory.memoryCounter = int(line)
                elif line_nr % 4 == 1:
                    self.memory.stateMemory[(line_nr - 1) // 4] = ast.literal_eval(line)
                elif line_nr % 4 == 2:
                    self.memory.actionMemory[(line_nr - 2) // 4] = ast.literal_eval(line)
                elif line_nr % 4 == 3:
                    self.memory.rewardMemory[(line_nr - 3) // 4] = float(line)
                else:
                    self.memory.newStateMemory[(line_nr - 4) // 4] = ast.literal_eval(line)
                line_nr += 1
