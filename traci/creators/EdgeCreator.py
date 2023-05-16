class EdgeCreator:
    FILENAME = "creators/sumo_files/app.edg.xml"
    TAB = "   "

    def __init__(self, nr_of_streets, edges):
        self.nr_of_streets = nr_of_streets
        self.edges = edges
        self.init_file()
        self.populate_file()
        self.end_file()

    def init_file(self):
        with open(self.FILENAME, "w") as edgesFile:
            print("""<?xml version="1.0" encoding="UTF-8"?>
<edges xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.sf.net/xsd/edges_file.xsd">""",
                  file=edgesFile)

    def end_file(self):
        with open(self.FILENAME, "a") as edgesFile:
            print("</edges>", file=edgesFile)

    def populate_file(self):
        with open(self.FILENAME, "a") as edgesFile:
            for edge in self.edges:
                if edge.lanes == 0:
                    continue

                fromPoint = str(edge.fromPoint)
                toPoint = str(edge.toPoint)
                id = edge.computeId()

                lanes = str(edge.lanes)
                edgeType = "T" + lanes

                print(
                    self.TAB + "<edge id=\"" + id + "\" from=\"" + fromPoint + "\" to=\"" + toPoint + "\" type=\"" + edgeType + "\"/>",
                    file=edgesFile)
