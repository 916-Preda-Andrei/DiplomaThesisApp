import random

import numpy as np

from training.Utils import Utils


class ReplayBuffer(object):
    def __init__(self, maxSize, inputShape, numberOfActions, discrete=False):
        self.memorySize = maxSize
        self.memoryCounter = [[0, 0, 0, 0] for _ in range(numberOfActions)]
        self.inputShape = inputShape
        self.discrete = discrete
        self.stateMemory = [[np.zeros((self.memorySize, inputShape)) for _ in range(numberOfActions)] for _ in range(numberOfActions)]
        self.newStateMemory = [[np.zeros((self.memorySize, inputShape)) for _ in range(numberOfActions)] for _ in range(numberOfActions)]
        self.actionMemory = [[np.zeros(self.memorySize) for _ in range(numberOfActions)] for _ in range(numberOfActions)]
        self.rewardMemory = [[np.zeros(self.memorySize) for _ in range(numberOfActions)] for _ in range(numberOfActions)]

    def storeTransition(self, state, action, reward, newState):
        phase = int(state[-1] - 1)
        index = self.memoryCounter[phase][action] % self.memorySize

        self.stateMemory[phase][action][index] = state
        self.newStateMemory[phase][action][index] = newState
        self.rewardMemory[phase][action][index] = reward
        self.actionMemory[phase][action][index] = action

        self.memoryCounter[phase][action] += 1

    def sampleBuffer(self, batchSize):
        maxMemory = self.memorySize
        for phase in range(4):
            for action in range(4):
                maxMemory = min(self.memoryCounter[phase][action], maxMemory)
        indexes = [i for i in range(maxMemory)]
        batch = random.sample(indexes, batchSize)

        states = self.stateMemory[batch]
        newStates = self.newStateMemory[batch]
        rewards = self.rewardMemory[batch]
        actions = self.actionMemory[batch]

        return states, actions, rewards, newStates

    def resize(self, preTraining):
        for phase in range(4):
            for action in range(4):
                if Utils.MEMORY_AFTER_UPDATE.value >= self.memoryCounter[phase][action]:
                    continue
                if preTraining:
                    indexes = [i for i in range(self.memoryCounter[phase][action])]
                    leftIndexes = random.sample(indexes, Utils.MEMORY_AFTER_UPDATE.value)
                else:
                    leftIndexes = [i % self.memorySize for i in range(self.memoryCounter[phase][action] - Utils.MEMORY_AFTER_UPDATE.value, self.memoryCounter[phase][action])]
                self.stateMemory[phase][action] = self.stateMemory[phase][action][leftIndexes]
                self.newStateMemory[phase][action] = self.newStateMemory[phase][action][leftIndexes]
                self.rewardMemory[phase][action] = self.rewardMemory[phase][action][leftIndexes]
                self.actionMemory[phase][action] = self.actionMemory[phase][action][leftIndexes]

                self.memoryCounter = Utils.MEMORY_AFTER_UPDATE.value

    def getAverageRewards(self):
        averageReward = np.zeros((4, 4))
        for phase in range(4):
            for action in range(4):
                if len(self.rewardMemory[phase][action]) > 0:
                    averageReward[phase][action] = np.average(self.rewardMemory[phase][action])
        return averageReward

    def getSampleFor(self, phase, action, preTraining):
        sampleSize = self.memoryCounter[phase][action]
        if preTraining:
            sampleSize = min(sampleSize, Utils.SAMPLE_SIZE_PRETRAIN.value)
        else:
            sampleSize = min(sampleSize, Utils.SAMPLE_SIZE.value)
        indexes = [i for i in range(self.memoryCounter[phase][action])]
        sampleIndexes = random.sample(indexes, sampleSize)

        return self.stateMemory[phase][action][sampleIndexes], self.actionMemory[phase][action][sampleIndexes], self.rewardMemory[phase][action][sampleIndexes], self.newStateMemory[phase][action][sampleIndexes]


