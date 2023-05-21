import os

import matplotlib.pyplot as plt

from training.Agent import Agent
from training.Environment import Environment
from training.Utils import Utils

if __name__ == "__main__":
    env = Environment()
    agent = Agent(alpha=Utils.ALPHA.value, gamma=Utils.GAMMA.value, numberOfActions=Utils.NUMBER_OF_ACTIONS.value,
                  batchSize=Utils.BATCH_SIZE.value,
                  inputDimensions=Utils.INPUT_DIMENSIONS.value, memorySize=Utils.MEMORY_SIZE.value,
                  filename=Utils.MODEL_FILENAME.value, memoryFilename=Utils.MEMORY_FILENAME.value, learningStepsToTake=Utils.LEARNING_STEPS.value)

    # agent.loadModel()

    scores = []

    for episode in range(Utils.EPISODES.value):
        print('Episode #', episode, ' started')
        agent.epsilon = 1.0 - (episode / Utils.EPISODES.value)
        done = False
        score = 0.0
        negativeReward = 0.0
        observation = env.reset()
        while not done:
            action = agent.chooseAction(observation)
            newObservation, reward, done, info = env.step(action)
            score += reward
            if reward < 0.0:
                negativeReward += reward
            agent.remember(observation, action, reward, newObservation)
            observation = newObservation
        env.runner.endConnection()
        print("Simulation #", episode, "ended")
        print("Learning...")
        agent.learn()
        print("Finished learning")
        scores.append(score)

        print('Episode #', episode, ' had negative reward %.2f' % negativeReward)

        if episode % 5 == 4:
            print("Saving model...")
            agent.saveModel()
            print("Model saved")

    filename = 'traffic_lights_optimization.png'

    plt.plot(scores)
    plt.ylabel('Scores')
    plt.xlabel('Episodes')
    plt.margins(0)
    minValue = min(scores)
    maxValue = max(scores)
    plt.ylim(minValue - 0.05 * abs(minValue), maxValue + 0.05 * abs(maxValue))
    fig = plt.gcf()
    fig.set_size_inches(20, 11.25)
    fig.savefig(os.path.join('plot', filename), dpi=96)
    plt.close("all")
