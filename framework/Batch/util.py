from deap import tools
import pickle
from results import LogBookTools


"""
Provides a set of tools for use with BatchJob logbook results.
"""

def saveLogbook(filePath, logbook):
    """
    Pickles and saves the given logbook to the file path specified. 

    :param filePath: File directory + name where to save the file.
    :param logbook: the logbook to save 
    """

    if(type(logbook) is not tools.Logbook):
        raise Exception("Paramater logbook must be of type Deap.tool.Logbook")

    with open(filePath, 'wb') as output:
        pickle.dump(logbook, output, pickle.HIGHEST_PROTOCOL)

def saveCSV(filePath, logbook):
    """
    Converts and saves the given logbook as a CSV to the file path specified. 
    The Logbook is converted to a column list with LogBookTools.logBookToListColumns() and then saved. When loaded again, it will be loaded into column list form (logbook object will not be preserved).

    :param filePath: File directory + name where to save the file.
    :param logbook: the logbook to save 
    """

    with open(filePath, 'wb') as output:
        listV = LogBookTools.logBookToListColumns(logbook)

        fileString = ""
        rows = 0

        for colName in listV:
            fileString += colName + ","
            if(rows == 0):
                rows = len(listV[colName])

        fileString = fileString[:-1]  # remove last comma
        fileString += "\n"

        for i in range(rows):
            for colName in listV:
                fileString += str(listV[colName][i]) + ","

            fileString = fileString[:-1]  # remove last comma
            fileString += "\n"

        output.write(fileString)

def loadLogbook(filePath):
    """
    Loads a pickled logbook object from the given filepath.

    returns the loaded Deap.tools.Logbook object
    """

    logbook = None
    with open(filePath, 'rb') as input:
        logbook = pickle.load(input)

    if(type(logbook) is not tools.Logbook):
        raise Exception("Loaded non-logbook")

    return logbook

def loadCSV(filePath):
    """
    Loads a CSV file into column list form. Refer to LogBookTools.logBookToListColumns().
    """

    colLists = {}
    with open(filePath, 'rb') as input:
        lines = input.readlines()

        colNames = lines[0].split(",")
        for i in range(len(colNames)):
            colNames[i] = colNames[i].strip()
            colLists[colNames[i]] = []

        for i in range(1, len(lines)):
            items = lines[i].split(",")
            for j in range(len(items)):
                colLists[colNames[j]].append(items[j].strip())

    return colLists
