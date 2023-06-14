import copy
import os

import matplotlib.pyplot as plt
import traci

from optimization.Agent import Agent
from controllers.Environment import Environment
from Utils import Utils

DEFAULT_SCHEDULE = [2, 2, 2, 2]

def getPicture(filename, data, yLabel, xLabel):
    plt.plot(data)
    plt.ylabel(yLabel)
    plt.xlabel(xLabel)
    plt.margins(0)
    minValue = min(data)
    maxValue = max(data)
    plt.ylim(minValue - 0.05 * abs(minValue), maxValue + 0.05 * abs(maxValue))
    fig = plt.gcf()
    fig.set_size_inches(20, 11.25)
    fig.savefig(os.path.join('plot', filename), dpi=96)
    plt.close("all")

def preTraining(env, agent):
    phaseCombinations = []
    for phase2 in range(1, 4):
        for phase3 in range(1, 4):
            if phase3 != phase2:
                for phase4 in range(1, 4):
                    if phase4 != phase3 and phase4 != phase2:
                        phaseCombinations.append([0, phase2, phase3, phase4])

    schedules = [DEFAULT_SCHEDULE]
    for dominantPhase in range(4):
        schedule = copy.deepcopy(DEFAULT_SCHEDULE)
        schedule[dominantPhase] -= 1
        schedules.append(schedule)
        for increaseBy in range(1, 4):
            schedule = copy.deepcopy(DEFAULT_SCHEDULE)
            schedule[dominantPhase] += increaseBy
            schedules.append(schedule)

    for phaseCombination in phaseCombinations:
        for schedule in schedules:
            print("Pre-episode with schedule", schedule, "and phase combination", phaseCombination, "started...")

            actionIndex = 0
            stepsTaken = 0
            done = False
            observation = env.reset(preTraining=True, training=True)

            while not done:
                action = phaseCombination[actionIndex]
                newObservation, reward, done = env.step(action)
                agent.remember(observation, action, reward, newObservation)
                observation = newObservation

                stepsTaken += 1
                if stepsTaken >= schedule[actionIndex]:
                    stepsTaken = 0
                    actionIndex = (actionIndex + 1) % 4

            env.runner.endConnection()
            print("Pre-episode ended.")

    agent.saveReplayBuffer()
    agent.updateNetwork(preTraining=True, useAverage=True)
    agent.updateNetworkBar(preTraining=True)

    return agent

if __name__ == "__main__":
    env = Environment()
    agent = Agent(alpha=Utils.ALPHA.value, numberOfActions=Utils.NUMBER_OF_ACTIONS.value,
                  batchSize=Utils.BATCH_SIZE.value,
                  inputDimensions=Utils.INPUT_DIMENSIONS.value, memorySize=Utils.MEMORY_SIZE.value,
                  filename=Utils.MODEL_FILENAME.value, memoryFilename=Utils.MEMORY_FILENAME.value,
                  learningStepsToTake=Utils.LEARNING_STEPS.value)

    if Utils.LOAD_MODEL.value:
        agent.loadModel()
    else:
        print("Starting pre-optimization...")
        agent = preTraining(env, agent)
        print("End pre-optimization")

    scores = []
    losses = []
    print("Starting optimization...")
    for learningStep in range(Utils.STARTING_STEP.value, Utils.LEARNING_STEPS.value):
        print("Learning step #", learningStep, "started.")
        done = False
        score = 0.0
        negativeReward = 0.0
        minLoss = float('inf')
        observation = env.reset(preTraining=False, training=True)
        counter = 0
        currentTime = 0
        while not done:
            action = agent.chooseAction(observation, traci.simulation.getTime())
            newObservation, reward, done = env.step(action)
            if env.runner.freshChanged:
                counter += 8
            else:
                counter += 5
            score += reward
            if reward < 0.0:
                negativeReward += reward
            agent.remember(observation, action, reward, newObservation)
            observation = newObservation

            if counter > Utils.UPDATE_PERIOD.value:
                currentTime += counter
                counter = 0
                print("Current time:", currentTime, "Learning step:", learningStep)
                minLoss = min(agent.updateNetwork(preTraining=False, useAverage=False), minLoss)
                agent.updateNetworkBar(preTraining=False)

        env.runner.endConnection()
        agent.saveModel()
        print('Learning step #', learningStep, ' had negative reward %.2f' % negativeReward)
        print('Learning step #', learningStep, ' had total reward %.2f' % score)
        print('Learning step #', learningStep, ' epsilon =', agent.epsilon)
        losses.append(minLoss)
        scores.append(score)
        print('Current scores:', scores)
        print('Current losses:', losses)

    print("Training ended.")

    getPicture('obtained_score.png', scores, 'Scores', 'Learning Steps')
    getPicture('obtained_loss.png', losses, 'Losses', 'Learning Steps')
