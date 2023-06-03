import copy
import os

import traci

from training.Agent import Agent
from training.Environment import Environment
from training.Utils import Utils

DEFAULT_SCHEDULE = [2, 2, 2, 2]


def preTraining(env, agent):
    phaseCombinations = []
    for phase2 in range(1, 4):
        for phase3 in range(1, 4):
            if phase3 != phase2:
                for phase4 in range(1,4):
                    if phase4 != phase3 and phase4!=phase2:
                        phaseCombinations.append([0, phase2, phase3, phase4])


    schedules = [DEFAULT_SCHEDULE]
    for dominantPhase in range(4):
        for increaseBy in range(1, 5):
            schedule = copy.deepcopy(DEFAULT_SCHEDULE)
            schedule[dominantPhase] += increaseBy
            schedules.append(schedule)

    for phaseCombination in phaseCombinations:
        for schedule in schedules:
            print("Pre-episode with schedule", schedule, "and phase combination", phaseCombination, "started...")
            actionIndex = 0
            stepsTaken = 0
            done = False
            env.setSchedule(schedule)
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
        print("Starting pre-training...")
        agent = preTraining(env, agent)
        print("End pre-training")

    # scores = []

    print("Starting training...")
    done = False
    score = 0.0
    negativeReward = 0.0
    observation = env.reset(preTraining=False, training=True)
    counter = 0
    while not done:
        action = agent.chooseAction(observation, traci.simulation.getTime())
        newObservation, reward, done = env.step(action)
        if env.runner.changedSemaphore:
            counter += 8
        else:
            counter += 5
        # score += reward
        # if reward < 0.0:
        #     negativeReward += reward
        agent.remember(observation, action, reward, newObservation)
        observation = newObservation

        if counter > Utils.UPDATE_PERIOD.value:
            counter = 0
            agent.updateNetwork(preTraining=False, useAverage=False)
            agent.updateNetworkBar(preTraining=False)

    print("Saving final model...")
    agent.saveModel()
    if Utils.SAVE_TO_DRIVE.value:
        os.system("mv dqn_model.h5 gdrive/MyDrive/")
        os.system("mv replay_buffer.txt gdrive/MyDrive/")
    print("Final model saved")

    env.runner.endConnection()
    print("Training ended.")
        # print("Learning...")
        # agent.learn()
        # print("Finished learning")
        # scores.append(score)
        #
        # print('Episode #', episode, ' had negative reward %.2f' % negativeReward)
        # print('Episode #', episode, ' had total reward %.2f' % score)

        # if episode % 5 == 4:
        #     print("Saving model...")
        #     agent.saveModel()
        #     if Utils.SAVE_TO_DRIVE.value:
        #         os.system("mv dqn_model.h5 gdrive/MyDrive/")
        #         os.system("mv replay_buffer.txt gdrive/MyDrive/")
        #     print("Model saved")

    # filename = 'traffic_lights_optimization.png'
    # plt.plot(scores)
    # plt.ylabel('Scores')
    # plt.xlabel('Episodes')
    # plt.margins(0)
    # minValue = min(scores)
    # maxValue = max(scores)
    # plt.ylim(minValue - 0.05 * abs(minValue), maxValue + 0.05 * abs(maxValue))
    # fig = plt.gcf()
    # fig.set_size_inches(20, 11.25)
    # fig.savefig(os.path.join('plot', filename), dpi=96)
    # plt.close("all")
