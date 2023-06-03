import copy
import random

import numpy as np

def _generate_pre_train_ratios(phase_min_time, em_phase):
    phase_traffic_ratios = [phase_min_time]

    # generate how many varients for each phase
    for i, phase_time in enumerate(phase_min_time):
        if i == em_phase:
            for j in range(1, 5, 1):
                gen_phase_time = copy.deepcopy(phase_min_time)
                gen_phase_time[i] += j
                phase_traffic_ratios.append(gen_phase_time)
        else:
            # pass
            for j in range(1, 5, 1):
                gen_phase_time = copy.deepcopy(phase_min_time)
                gen_phase_time[i] += j
                phase_traffic_ratios.append(gen_phase_time)
        for j in range(5, 20, 5):
            gen_phase_time = copy.deepcopy(phase_min_time)
            gen_phase_time[i] += j
            phase_traffic_ratios.append(gen_phase_time)

    return phase_traffic_ratios

# print(_generate_pre_train_ratios([10, 10], 0))
print(random.sample([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], 10))