import unittest
from model.State import State


class StateTest(unittest.TestCase):
    state = None

    @classmethod
    def setUpClass(cls):
        carsForLane = {}
        waitingForLane = {}
        queueForLane = {}
        for street in range(1, 5):
            for lane in range(0, 3):
                laneId = "E_" + str(street) + "_0_" + str(lane)
                carsForLane[laneId] = street * lane
                waitingForLane[laneId] = street * lane
                queueForLane[laneId] = street * lane
        cls.state = State(carsForLane, waitingForLane, queueForLane, 1, False)

    def test_creation(self):
        index = 0

        # Cars present on lane part
        for street in range(1, 5):
            for lane in range(0, 3):
                self.assertEqual(self.state.stateList[index], street * lane)
                index += 1

        # Total waiting on lane part
        for street in range(1, 5):
            for lane in range(0, 3):
                self.assertEqual(self.state.stateList[index], street * lane)
                index += 1

        # Queue length on lane part
        for street in range(1, 5):
            for lane in range(0, 3):
                self.assertEqual(self.state.stateList[index], street * lane)
                index += 1

        # Current phase part
        self.assertEqual(self.state.stateList[index], 2)
        index += 1

        # Is a fresh change of the semaphore part
        self.assertEqual(self.state.stateList[index], 0)
