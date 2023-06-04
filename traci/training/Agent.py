import ast
import json
import os
from json import JSONEncoder

import numpy as np
from keras.layers import Dense, Activation
from keras.models import Sequential, load_model, clone_model
from keras.optimizers import Adam, RMSprop
from keras.callbacks import EarlyStopping
from model.MoveType import MoveType
from training.ReplayBuffer import ReplayBuffer
from training.Utils import Utils


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


def buildDQN(learningRate, numberOfActions, inputDimensions, firstFullyConnectedLayerDimensions,
             secondFullyConnectedLayerDimensions):
    model = Sequential([
        Dense(firstFullyConnectedLayerDimensions, input_shape=(inputDimensions,)),
        Activation('sigmoid'),
        Dense(secondFullyConnectedLayerDimensions),
        Activation('sigmoid'),
        Dense(numberOfActions, activation='linear'),
    ])
    model.compile(optimizer=RMSprop(lr=learningRate), loss='mse')
    model.summary()
    return model

def unison_shuffled_copies(Xs, Y, sample_weight):
    p = np.random.permutation(len(Y))
    new_Xs = Xs[p]
    return new_Xs, Y[p], sample_weight[p]

class Agent(object):


    def __init__(self, alpha, numberOfActions, batchSize, inputDimensions, memorySize, filename, memoryFilename,
                 learningStepsToTake):
        self.actionSpace = [move.value for move in MoveType]
        self.numberOfActions = numberOfActions
        self.epsilon = 0.05
        self.epsilonDecrease = 0.9999
        self.epsilonMin = 0.001
        self.batchSize = batchSize
        self.modelFile = filename
        self.memoryFile = memoryFilename
        self.alpha = alpha
        self.memory = ReplayBuffer(memorySize, inputDimensions, numberOfActions, discrete=True)
        self.qEval = buildDQN(alpha, numberOfActions, inputDimensions, 20, 20)
        self.qEval_bar = None
        self.buildFromMainNetwork()
        self.q_bar_outdated = 0
        self.inputDimensions = inputDimensions
        self.learningStepsToTake = learningStepsToTake

    def remember(self, state, action, reward, newState):
        self.memory.storeTransition(state, action, reward, newState)

    def chooseAction(self, state, currentTime):
        rand = np.random.random()
        if rand <= self.epsilon:
            action = np.random.choice(self.actionSpace)
        else:
            actions = self.qEval.predict([state], verbose=None)
            action = np.argmax(actions)

        if self.epsilon > self.epsilonMin and currentTime >= 5000:
            self.epsilon = self.epsilon * self.epsilonDecrease

        return action

    def chooseBestAction(self, state):
        actions = self.qEval.predict([state], verbose=None)
        return np.argmax(actions)


    def updateNetwork(self, preTraining, useAverage):
        gamma = Utils.GAMMA_PRETRAIN.value
        if not preTraining:
            gamma = Utils.GAMMA.value

        averageReward = self.memory.getAverageRewards()

        states = []
        Y = []
        for phase in range(4):
            for action in range(4):
                y, statesFromSample = self.getSample(gamma, phase, action, preTraining, averageReward[phase], useAverage)
                Y.extend(y)
                for state in statesFromSample:
                    states.append(state)

        Xs = np.array(states)
        Y = np.array(Y)
        sampleWeight = np.ones(len(Y))
        Xs, Y, _ = unison_shuffled_copies(Xs, Y, sampleWeight)

        self.trainNetwork(Xs, Y, preTraining)
        self.q_bar_outdated += 1

        self.memory.resize(preTraining)

    def saveModel(self):
        print("Saving model...")
        self.qEval.save(self.modelFile)
        if Utils.SAVE_TO_DRIVE.value:
            os.system("mv dqn_model.h5 gdrive/MyDrive/")
        print("Model saved")
        self.saveReplayBuffer()

    def saveReplayBuffer(self):
        print("Saving replay memory...")
        with open(self.memoryFile, "w") as memory:
            for phase in range(4):
                for action in range(4):
                    print(self.memory.memoryCounter[phase][action], file=memory)
                    for i in range(self.memory.memorySize):
                        print(json.dumps(self.memory.stateMemory[phase][action][i], cls=NumpyArrayEncoder), file=memory)
                        print(json.dumps(self.memory.actionMemory[phase][action][i], cls=NumpyArrayEncoder), file=memory)
                        print(self.memory.rewardMemory[phase][action][i], file=memory)
                        print(json.dumps(self.memory.newStateMemory[phase][action][i], cls=NumpyArrayEncoder), file=memory)
        if Utils.SAVE_TO_DRIVE.value:
            os.system("mv replay_buffer.txt gdrive/MyDrive/")
        print("Replay memory saved.")

    def loadModel(self):
        self.qEval = load_model(self.modelFile)
        if Utils.LOAD_REPLAY_BUFFER.value:
            self.loadReplayMemory()

    def loadReplayMemory(self):
        print("Loading replay memory...")
        with open(self.memoryFile) as memory:
            line_nr = 0
            lines = [line for line in memory]
            for phase in range(4):
                for action in range(4):
                    line = lines[line_nr]
                    line_nr += 1
                    self.memory.memoryCounter[phase][action] = int(line)
                    for i in range(self.memory.memorySize):
                        line = lines[line_nr]
                        line_nr += 1
                        self.memory.stateMemory[phase][action][i] = ast.literal_eval(line)

                        line = lines[line_nr]
                        line_nr += 1
                        self.memory.actionMemory[phase][action][i] = ast.literal_eval(line)

                        line = lines[line_nr]
                        line_nr += 1
                        self.memory.rewardMemory[phase][action][i] = float(line)

                        line = lines[line_nr]
                        line_nr += 1
                        self.memory.newStateMemory[phase][action][i] = ast.literal_eval(line)
        print("Replay memory loaded.")

    def getSample(self, gamma, phase, action, preTraining, averageReward, useAverage):
        states, actions, rewards, newStates = self.memory.getSampleFor(phase, action, preTraining)
        Y = []
        howmany = len(states)

        for i in range(howmany):
            state = states[i]
            action = actions[i]
            reward = rewards[i]
            newState = newStates[i]

            nextReward = self.getNextEstimatedReward(newState)
            totalReward = reward + gamma * nextReward

            if not useAverage:
                input_data = np.reshape(state, (1, 37))
                target = self.qEval.predict([input_data], verbose=None)
            else:
                target = np.copy(np.array([averageReward]))

            target[0][int(action)] = totalReward
            Y.append(target[0])
        return Y, states

    def trainNetwork(self, Xs, Y, preTraining):

        episodes = Utils.PRE_TRAINING_EPISODES.value if preTraining else Utils.EPISODES.value
        batchSize = min(self.batchSize, len(Y))
        earlyStopping = EarlyStopping(monitor='val_loss', patience=10, verbose=0, mode='min')
        print("Training the network...")
        self.qEval.fit(Xs, Y, batch_size=batchSize, epochs=episodes, shuffle=False, verbose=1, validation_split=0.3, callbacks=[earlyStopping])
        print("Network trained.")
        if preTraining:
            self.saveModel()

    def getNextEstimatedReward(self, nextState):
        input_data = np.reshape(nextState, (1, 37))
        return np.max(self.qEval_bar.predict_on_batch([input_data]))

    def buildFromMainNetwork(self):
        self.qEval_bar = clone_model(self.qEval)
        self.qEval_bar.set_weights(self.qEval.get_weights())
        self.qEval_bar.compile(optimizer=RMSprop(lr=self.alpha), loss='mse')

    def updateNetworkBar(self, preTraining=False):
        if self.q_bar_outdated >= Utils.UPDATE_WITH_TARGET.value or preTraining:
            self.q_bar_outdated = 0
            self.buildFromMainNetwork()
