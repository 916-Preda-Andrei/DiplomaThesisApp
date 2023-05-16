import numpy as np

from model.MoveType import MoveType
from training.ReplayBuffer import ReplayBuffer
from keras.layers import Dense, Activation
from keras.models import Sequential, load_model
from keras.optimizers import Adam

def buildDQN(learningRate, numberOfActions, inputDimensions, firstFullyConnectedLayerDimensions, secondFullyConnectedLayerDimensions):
    model = Sequential([
        Dense(firstFullyConnectedLayerDimensions, input_shape=(inputDimensions, )),
        Activation('relu'),
        Dense(secondFullyConnectedLayerDimensions),
        Activation('relu'),
        Dense(numberOfActions),
        Activation('relu')
    ])

    model.compile(optimizer=Adam(learning_rate=learningRate), loss='mse')
    return model

class Agent(object):
    def __init__(self, alpha, gamma, numberOfActions, epsilon, batchSize, inputDimensions, epsilonDecrease, epsilonEnd, memorySize, filename):
        self.actionSpace = [move.value for move in MoveType]
        self.numberOfActions = numberOfActions
        self.gamma = gamma

        self.epsilon = epsilon
        self.epsilonDecrease = epsilonDecrease
        self.epsilonMin = epsilonEnd
        self.batchSize = batchSize
        self.modelFile = filename
        self.memory = ReplayBuffer(memorySize, inputDimensions, numberOfActions, discrete=True)
        self.qEval = buildDQN(alpha, numberOfActions, inputDimensions, 256, 256)

    def remember(self, state, action, reward, newState, done):
        self.memory.storeTransition(state, action, reward, newState, done)

    def chooseAction(self, state):
        rand = np.random.random()
        if rand < self.epsilon:
            action = np.random.choice(self.actionSpace)
        else:
            actions = self.qEval.predict([state], verbose=None)
            action = np.argmax(actions)
        #TODO:check when running
        return action

    def chooseBestAction(self, state):
        actions = self.qEval.predict([state])
        #TODO:check above function
        return np.argmax(actions)

    def learn(self):
        if self.memory.memoryCounter < self.batchSize:
            return
        state, action, reward, newState, done = self.memory.sampleBuffer(self.batchSize)

        actionValues = np.array(self.actionSpace, dtype=np.int8)
        actionIndices = np.dot(action, actionValues)

        qEval = self.qEval.predict([state], verbose=None)
        qNext = self.qEval.predict([newState], verbose=None)

        qTarget = qEval.copy()

        batchIndex = np.arange(self.batchSize, dtype=np.int32)

        qTarget[batchIndex, actionIndices] = reward + self.gamma * np.max(qNext, axis=1) * done

        _ = self.qEval.fit([state], qTarget, verbose=0)

        self.epsilon = max(self.epsilon*self.epsilonDecrease, self.epsilonMin)

    def saveModel(self):
        self.qEval.save(self.modelFile)
        print("Epsilon=", str(self.epsilon))

    def loadModel(self):
        self.qEval = load_model(self.modelFile)