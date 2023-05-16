import os

import numpy as np
import matplotlib.pyplot as plt

from training.Agent import Agent
from training.Environment import Environment
from training.Utils import Utils

if __name__ == "__main__":
    env = Environment()
    agent = Agent(alpha=Utils.ALPHA.value, gamma=Utils.GAMMA.value, numberOfActions=Utils.NUMBER_OF_ACTIONS.value,
                  epsilon=0.01, batchSize=Utils.BATCH_SIZE.value,
                  inputDimensions=Utils.INPUT_DIMENSIONS.value, epsilonDecrease=Utils.EPSILON_DECREASE.value,
                  epsilonEnd=Utils.EPSILON_END.value, memorySize=Utils.MEMORY_SIZE.value,
                  filename=Utils.MODEL_FILENAME.value)

    agent.loadModel()

    scores = []
    epsilonHistory = []

    for i in range(40, Utils.EPISODES.value):
        print('Episode #', i, ' started')
        done = False
        score = 0
        observation = env.reset()
        while not done:
            action = agent.chooseAction(observation)
            newObservation, reward, done, info = env.step(action)
            score += reward
            agent.remember(observation, action, reward, newObservation, done)
            observation = newObservation
            agent.learn()
        env.runner.endConnection()

        epsilonHistory.append(agent.epsilon)
        scores.append(score)

        avgScore = np.mean(scores[max(0, i-100):(i+1)])
        print('Episode #', i, ' score %.2f' % score,
              'average score %.2f' % avgScore)

        if i%10 == 9:
            agent.saveModel()

    filename = 'traffic_lights_optimization.png'
    x = [i+1 for i in range(Utils.EPISODES.value)]

    plt.plot(scores)
    plt.ylabel('Scores')
    plt.xlabel('Episodes')
    plt.margins(0)
    minValue = min(scores)
    maxValue = max(scores)
    plt.ylim(minValue - 0.05 * abs(minValue), maxValue + 0.05 * abs(maxValue))
    fig = plt.gcf()
    fig.set_size_inches(20, 11.25)
    fig.savefig(os.path.join('plot_',filename), dpi=96)
    plt.close("all")