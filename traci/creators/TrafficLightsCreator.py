from model.MoveType import MoveType
from training.Utils import Utils

NSR1_GREEN = "GGrrrrGGrrrr"
NSR1_YELLOW = "yyrrrryyrrrr"
WER2_GREEN = "rrrGGrrrrGGr"
WER2_YELLOW = "rrryyrrrryyr"
L1R1_GREEN = "GrrrrGGrrrrG"
L1R1_YELLOW = "yrrrryyrrrry"
L2R2_GREEN = "rrGGrrrrGGrr"
L2R2_YELLOW = "rryyrrrryyrr"

PHASES_MOVE_TYPE = {
    MoveType.NSR1: [NSR1_GREEN, NSR1_YELLOW],
    MoveType.WER2: [WER2_GREEN, WER2_YELLOW],
    MoveType.L1R1: [L1R1_GREEN, L1R1_YELLOW],
    MoveType.L2R2: [L2R2_GREEN, L2R2_YELLOW]
}

class TrafficLightsCreator:
    FILENAME = "creators/sumo_files/app.program.xml"
    TAB = "   "

    def __init__(self, semaphoreDuration):
        self.semaphoreDuration = semaphoreDuration
        self.init_file()
        self.populate_file()
        self.end_file()

    def init_file(self):
        with open(self.FILENAME, "w") as program_file:
            print("""<additional>
    <tlLogic id ="0" programID="trafficLightsProgram" offset="0" type="static">""",
                  file=program_file)

    def end_file(self):
        with open(self.FILENAME, "a") as program_file:
            print("""    </tlLogic>
</additional>""", file=program_file)

    def populate_file(self):
        with open(self.FILENAME, "a") as program_file:
            for moveType in Utils.MOVE_TYPES_IN_ORDER.value:
                greenPhase = PHASES_MOVE_TYPE[moveType][0]
                duration = str(self.semaphoreDuration[moveType])
                print(self.TAB * 2 + "<phase duration=\"" + duration + "\" state=\"" + greenPhase + "\"/>", file=program_file)

                yellowPhase = PHASES_MOVE_TYPE[moveType][1]
                duration = str(Utils.YELLOW_LIGHT.value)
                print(self.TAB * 2 + "<phase duration=\"" + duration + "\" state=\"" + yellowPhase + "\"/>", file=program_file)
