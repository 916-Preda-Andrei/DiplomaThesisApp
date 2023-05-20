import numpy as np

from training.Utils import Utils


class ReplayBuffer(object):
    def __init__(self, maxSize, inputShape, numberOfActions, discrete=False):
        self.memorySize = maxSize
        self.memoryCounter = 0
        self.inputShape = inputShape
        self.discrete = discrete
        self.stateMemory = np.zeros((self.memorySize, inputShape))
        self.newStateMemory = np.zeros((self.memorySize, inputShape))
        self.dType = np.int8 if self.discrete else np.float32
        self.actionMemory = np.zeros((self.memorySize, numberOfActions), dtype=self.dType)
        self.rewardMemory = np.zeros(self.memorySize)

    def storeTransition(self, state, action, reward, newState):
        index = self.memoryCounter % self.memorySize
        self.stateMemory[index] = state
        self.newStateMemory[index] = newState
        self.rewardMemory[index] = reward

        if self.discrete:
            actions = np.zeros(self.actionMemory.shape[1])
            actions[action] = 1.0
            self.actionMemory[index] = actions
        else:
            self.actionMemory[index] = action
        self.memoryCounter += 1

    def sampleBuffer(self, batchSize):
        maxMemory = min(self.memoryCounter, self.memorySize)
        batch = np.random.choice(maxMemory, batchSize)

        states = self.stateMemory[batch]
        newStates = self.newStateMemory[batch]
        rewards = self.rewardMemory[batch]
        actions = self.actionMemory[batch]

        return states, actions, rewards, newStates

