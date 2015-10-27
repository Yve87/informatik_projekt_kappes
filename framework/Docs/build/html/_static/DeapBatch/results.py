
import sys
import copy
import logging
from deap import tools
import MySQLdb as mdb


class Filter(dict):

    """
        Filters data to usable row/columns. Can handle types Database(), Logbook(), JobResult[], Filter[], or a columnList (a dict or lists).



    """

    def __init__(self, data, *colNames, **specifics):
        """
            Filters specific columns and rows (like a DB select). *colnames is a list of the names of the colomns that will be returned. 

            If **specifics is checked, the row values of other columns can be checked for equivalence to a specific value. Does an 'and' operation on values set in **specifics.

            :param data: Three data types accepted: Database(), Logbook(), JobResult[], Filter[], or a columnList (a dict or lists)
            :param colNames: list of strings containing the names of the columns that will be returned
            :param specifics: Dict containing name-value pairs. When the filter() is made, the rows that do not contain all the **specifics values will not be included.

            Example:
                filteredData = dataFilter.filter("name", "val", result_gen=5)
                will return a data set containing the value and average items of rows where gen=5

        """

        if isinstance(data, tools.Logbook):
            listCols = LogBookTools.logBookToListColumns(data)
            print listCols
            filtered = Filter.__filter(listCols, *colNames, **specifics)
            self.update(filtered)

        elif isinstance(data, DatabaseResults):
            filtered = data.select(*colNames, **specifics)
            self.update(filtered)

        elif isinstance(data, list):  # JobResult List
            logbook = createSuperLogbook(data)
            listCols = LogBookTools.logBookToListColumns(logbook)
            filtered = Filter.__filter(listCols, *colNames, **specifics)
            self.update(filtered)

        elif isinstance(data, (Filter, dict)):
            filtered = Filter.__filter(data, *colNames, **specifics)
            self.update(filtered)
        else:
            raise Exception("Unfilterable datatype '" + str(type(data)) + "'")

    @staticmethod
    def __filter(colList, *colNames, **specifics):
        """
            Filters specific columns and rows (like a DB select). *colnames is a list of the names of the colomns that will be returned. 

            If **specifics is checked, the row values of other columns can be checked for equivalence to a specific value. Does an 'and' operation on values set in **specifics.

            :param colNames: list of strings containing the names of the columns that will be returned
            :param specifics: Dict containing name-value pairs. When the filter() is made, the rows that do not contain all the **specifics values will not be included.

            Example:
                filteredData = dataFilter.filter("name", "val", result_gen=5)
                will return a data set containing the value and average items of rows where gen=5
        """
        filtered = {}

        if len(colNames) == 0:
            # no columns specified, so return all
            colNames = colList.keys()

        if(len(specifics) > 0):
            # specifics were specified. Isolate columns that will and grab only the rows with values that match **specifics assignments. i.e if specifics= {'results_gen':3} then the rows that satisfy results_gen=3 AND belong to *colNames will be added to the filtered object.

            validIndexes = []
            firstRound = True
            for colName in specifics:
                colData = colList[colName]
                for i in range(len(colData)):
                    if colData[i] == specifics[colName]:
                        if(firstRound):
                            validIndexes.append(i)
                        else:
                            if i not in validIndexes:
                                try:
                                    validIndexes.remove(i)
                                except ValueError:
                                    pass
                    else:
                        try:
                            validIndexes.remove(i)
                        except ValueError:
                            pass

                firstRound = False

            for colName in colNames:
                colData = colList[colName]
                filtered[colName] = []
                for i in range(len(validIndexes)):
                    filtered[colName].append(colData[validIndexes[i]])
        else:
            # no specifics so all rows are valid. Doesnt use validIndexes[]
            # just return an object containing references to original arrays

            for colName in colNames:
                filtered[colName] = colList[colName]

        return filtered


class DatabaseResults:

    """
    Connects to stored results in a specific database table.
    Warning: DatabaseResults.persistRun() will override any previous table with the same name
    """

    def __init__(self, host, user, password, database, table, port=None):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.table = table
        self.port = port

    def select(self, *colNames, **specifics):
        """
        DB selects specific columns and rows. 

        :param colNames: List of strings containing the names of the columns that will be returned
        :param specifics: Dict containing name-value pairs. When the select() is made, the rows that do not contain all the **specifics values will not be included.

        Example:
                filteredData = databaseHandler.select("name", "val", result_gen=5, result_max=300)
                will return a data set containing the value and average items of rows where result_gen=5 and result_max=300
                Euivalent to the query: "SELECT name,val FROM aTable WHERE result_gen=5 AND result_max=300;"
        """

        # if(colNames == None):
        #     raise Exception("At least one column name (*colNames) must be specified.")

        listCols = {}
        con = None
        try:
            con = mdb.connect(self.host, self.user, self.password, self.database)
            cur = con.cursor()
            selString = 'SELECT '

            if(len(colNames) > 0):
                for colName in colNames:
                    selString += colName + ','
                selString = selString[:-1]
            else:
                selString += "* "
            selString += ' FROM ' + self.table + ' '

            if(len(specifics) > 0):
                selString += 'WHERE '
                for spec in specifics:
                    if isinstance(specifics[spec], float):
                        selString += 'ABS(' + spec + " - " + str(specifics[spec]) + ") < 1e-6"
                    else:
                        selString += spec + " = " + str(specifics[spec])
                    selString += ' AND '
                selString = selString[:-4]

            if(len(selString) > 100):
                logging.debug(selString[:100])
            else:
                logging.debug(selString)
            cur.execute(selString)

            data = cur.fetchall()

            columnsPulled = []
            for tpl in cur.description:
                columnsPulled.append(tpl[0])

            # convert data to listColumns
            for row in data:
                for i in range(len(row)):
                    if listCols.get(columnsPulled[i]) == None:
                        listCols[columnsPulled[i]] = []
                    listCols[columnsPulled[i]].append(row[i])

        except mdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            sys.exit(1)
        finally:
            if(con):
                con.close()

        return listCols

    def persistRun(self, batchJob, callback=None):
        """
        Runs the given BatchJob object and puts the results in the Database concurrently.
        Jobs must have unique job_ids (BatchJob does this by default).
        uses BatchJob.run_async_ind()

        :param batchJob: BatchJob object to run
        :param callback: callback function called after every job is complete and added to the DB. format: callback(jobResult)
        """

        try:
            con = mdb.connect(self.host, self.user, self.password, self.database)
            cur = con.cursor()
            cur.execute("DROP TABLE IF EXISTS " + self.table)

            def indJobDone(jobResult):
                newLogbook = LogBookTools.createLogbookFrom(jobResult)
                colList = LogBookTools.logBookToListColumns(newLogbook)

                cur.execute("START TRANSACTION")
                if cur.execute("SHOW TABLES LIKE '" + self.table + "'") == 0:  # create the table
                    tableCreated = True
                    crString = "CREATE TABLE " + self.table + "("
                    crString += "iID INT PRIMARY KEY AUTO_INCREMENT,"

                    for colName in colList:
                        crString += str(colName) + " "
                        if isinstance(colList[colName][0], (int, long)):
                            crString += "INTEGER"
                        elif isinstance(colList[colName][0], (float, complex)):
                            crString += "FLOAT"
                        else:
                            crString += "VARCHAR(30)"

                        crString += ","

                    crString = crString[:-1]  # remove last comma
                    crString += ")"
                    logging.debug(crString)
                    cur.execute(crString)

                insString = "INSERT INTO " + self.table + " (iId,"
                for colName in colList:
                    insString += colName + ","
                insString = insString[:-1]  # remove last comma
                insString += ")"
                insString += " VALUES "

                firstCol = colList.itervalues().next()

                # add the row
                for i in range(len(firstCol)):
                    insString += " (DEFAULT,"
                    for colName in colList:
                        if(isinstance(colList[colName][i], str)):
                            insString += "'" + colList[colName][i] + "',"
                        else:
                            insString += str(colList[colName][i]) + ","
                    insString = insString[:-1]
                    insString += "),"
                insString = insString[:-1]

                if(len(insString) > 100):
                    logging.debug(insString[:100])
                else:
                    logging.debug(insString)
                cur.execute(insString)
                con.commit()
                if callback != None:
                    callback(jobResult)

            batchJob.run_async_ind(indJobDone)

        except mdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            sys.exit(1)
        finally:
            if(con):
                con.close()


class LogBookTools:

    """
        Static class. Contains a set of tools for handling multiple logbooks.
    """

    @staticmethod
    def logBookToListColumns(logbook, subName=None, processedData=None):
        """
            Recursivly processes the logbook into easy to use column lists.

            Returns a dict with item key of the column names and values being a list.
            Chapters will be 'pushed up' so that there is only one layer of dictionary (i.e no more dict within a dict). The names of the columns are a combination of the parent chapter names seperated by '_'.

            For Example,
            Calling LogBookTools.logBookToListColumns() with the following logbook:

                  fitness
                -------------
            gen min  max  avg
            0   1100 1200 1150
            1   1105 1210 1153
            2   1101 1250 1156

            would return the following dictionary:

            {
                gen:[0,1,2],
                fitness_min:[1100,1105,1101],
                fitness_max:[1200,1210,1250],
                fitness_avg:[1150, 1153, 1156]
            }


        """

        if(processedData == None):
            processedData = {}

        for item in logbook:
            for key in item:
                columnName = key
                if(subName != None):
                    columnName = subName + "_" + key

                if(processedData.get(columnName) == None):
                    processedData[columnName] = []
                processedData[columnName].append(item[key])

        for chName in logbook.chapters:
            newSubName = chName
            if subName != None:
                newSubName = subName + "_" + chName
            LogBookTools.logBookToListColumns(logbook.chapters[chName], newSubName, processedData)

        return processedData

    @staticmethod
    def appendLogbookRecursive(toLogbook, fromLogbook):
        """
            Appends fromLogbook's data into toLogbook. Logbook formats must be the same
        """
        # add all columns
        for item in fromLogbook:
            toLogbook.record(**item)
        # call recursively for chapters
        for chName in fromLogbook.chapters:
            LogBookTools.appendLogbookRecursive(toLogbook.chapters[chName], fromLogbook.chapters[chName])

    @staticmethod
    def averageLogbookValues(logbooks):
        """
            Returns a new logbook containing the average values of all the cells from all the given logbooks.

            Values which are confilicting (i.e cannot average two strings) will be set to the value of the last given logbook.

            :param logbooks: The list of Deap.tools.Logbooks to average
        """
        newLogbook = tools.Logbook()

        averagedItems = []
        for rowI in range(len(logbooks[0])):
            # rowI is the row index
            averagedItems.append({})

            for logbook in logbooks:
                for key, val in logbook[rowI].iteritems():
                    if(isinstance(val, (int, long, float, complex))):
                        if averagedItems[rowI].get(key) == None:
                            averagedItems[rowI][key] = val
                        else:
                            averagedItems[rowI][key] += val
                    else:
                        averagedItems[rowI][key] = val  # will end up just taking the value from the last logbook

            for key, val in averagedItems[rowI].iteritems():
                if(isinstance(val, (int, long, float, complex))):
                    averagedItems[rowI][key] /= float(len(logbooks))
            newLogbook.record(**averagedItems[rowI])

        for chapterName in logbooks[0].chapters:
            chapterList = []
            for logbook in logbooks:  # compile all the chapters to average into a list
                chapterList.append(logbook.chapters[chapterName])

            newLogbook.chapters[chapterName] = LogBookTools.averageLogbookValues(chapterList)

        return newLogbook

    @staticmethod
    def combineLogbooks(logbooks):
        """
            Creates a new Logbook containing the contents of both given Logbooks. Logbook structure should be identical
        """
        newLogbook = tools.Logbook()

        for logbook in logbooks:
            LogBookTools.appendLogbookRecursive(newLogbook, logbook)

        return newLogbook

    @staticmethod
    def createSuperLogbook(jobResults):
        logbooks = []
        for result in jobResults:
            logbooks.append(LogBookTools.createLogbookFrom(result))
        return LogBookTools.combineLogbooks(logbooks)

        # add items from both logbooks to newLogbook
    @staticmethod
    def createLogbookFrom(jobResult):
        """
            Creates a logbook from the given jobResult object by appending the job info to each row in the logbook in jobResult.logbook

            Returns a new Deap.tools.Logbook instance
        """

        if isinstance(jobResult.logbook, tools.Logbook):
            newLogbook = tools.Logbook()

            for i in range(len(jobResult.logbook)):
                newLogbook.record(**jobResult.job.execParams)
            newLogbook.chapters['result'] = jobResult.logbook
        else:
            # cannot be added
            raise ValueError('The logbook from this job cannot be processed into a logbook: ' + str(jobResult.logbook))

        return newLogbook
    """
    createFullLogbook():
                           data                                   job
    ------------------------------------------------------  ---------------
                         fitness                 size
                -------------------------  ---------------
    gen   evals min      avg      max      min   avg   max   cxpb   ngen
    0     30    0.165572 1.71136  6.85956  3     4.54  7     0.1    10
    1     30    0.165572 1.71136  6.85956  3     4.54  7     0.1    10
    2     30    0.165572 1.71136  6.85956  3     4.54  7     0.1    10
    3     30    0.165572 1.71136  6.85956  3     4.54  7     0.1    10
    0     30    0.165572 1.71136  6.85956  3     4.54  7     0.2    10
    1     30    0.165572 1.71136  6.85956  3     4.54  7     0.2    10
    2     30    0.165572 1.71136  6.85956  3     4.54  7     0.2    10
    3     30    0.165572 1.71136  6.85956  3     4.54  7     0.2    10




    jobResults logbook:
                         fitness                 size
                -------------------------  ---------------
    gen   evals min      avg      max      min   avg   max
    0     30    0.165572 1.71136  6.85956  3     4.54  7
    1     30    0.165572 1.71136  6.85956  3     4.54  7
    2     30    0.165572 1.71136  6.85956  3     4.54  7
    3     30    0.165572 1.71136  6.85956  3     4.54  7
    4     30    0.165572 1.71136  6.85956  3     4.54  7
    5     30    0.165572 1.71136  6.85956  3     4.54  7
    6     30    0.165572 1.71136  6.85956  3     4.54  7
    7     30    0.165572 1.71136  6.85956  3     4.54  7
    8     30    0.165572 1.71136  6.85956  3     4.54  7
    9     30    0.165572 1.71136  6.85956  3     4.54  7
    """


class Util:

    """
    Provides a set of tools for use with BatchJob logbook results.
    """

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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
