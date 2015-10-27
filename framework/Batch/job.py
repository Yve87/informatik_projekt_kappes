import sys
import inspect
import logging
import itertools
from results import LogBookTools
from multiprocessing import Pool
import time


class JobTemplate:

    """
        JobTemplate is a wrapper for a given delegate function named the makerFunction. When run by a job, the makerfunction is called with the jobs specific execParams as paramaters.
        Also contains defaults for values that are not set by the Job instance.

        The default for "number_of_runs" is automatically set to 1
    """

    def __init__(self, makerFunction):
        self.defaults = {}
        self.defaults["number_of_runs"] = 1
        self.setMakerFunction(makerFunction)

    def setMakerFunction(self, makerFunction):
        """
            Set the Maker function for this JobTemplate. When run by a job, the makerfunction is called with the jobs specific execParams as paramaters.

            :param makerFunction: The function called on Job.run()
            The maker function must have the following function prototype:

                def someJobFunction(**params):
                    ...
                    return (logbook, results)

            The function must return a tuple, where 'logbook' is the final Deap.tools.LogBook for the data obtained in the function and 'results' is any object which might be used by the user externally. 

            When the Job is executed with Job.run(), the (logbook, result) tuple is put into the JobResult object returned by the Job.

            ***Important:
                The makerFunction passed into this function must be picklable if it is to be used by BatchJob.
                Defining the makerFunction in the global scope will usually ensure it is picklable (unless it has some wierd references).

        """
        # check to see if the given function format is okay
        funcInfo = inspect.getargspec(makerFunction)

        if(len(funcInfo.args) == 0 and funcInfo.varargs == None and funcInfo.keywords != None and funcInfo.defaults == None):
            self.makerFunction = makerFunction
        else:
            raise Exception("Improper maker function prototype. See JobTemplate.setMakerFunction()")

    def setDefaults(self, **kwargs):
        """
            Sets the default paramater values to set if they are not specified by the executing Job's execParams. Params set by the job have higher precedence over default paramaters and therefore, if set, will override default paramater values.
        """
        self.defaults = kwargs
        if(self.defaults.get("number_of_runs") == None):
            self.defaults["number_of_runs"] = 1

    def run(self, **kwargs):
        """
            Executes the makerFunction with the given paramaters. Sets the given paramaters with precidence over the defaults 
        """
        params = {}

        # set defaults if they are not already set in kwargs
        for key in self.defaults:
            if(kwargs.get(key) == None):
                kwargs[key] = self.defaults[key]

        # execute maker function
        self.makerFunction(**kwargs)

    def __str__(self):
        return self.makerFunction.__name__


class Job:

    """
        A Job is a container for a set of execution paramaters to be used on a JobTemplate. A Job can only be run once. Used by BatchJob to execute multiple Jobs concurrently.
    """

    def __init__(self, jobTempate, **execParams):
        """
            Initialized the Job.


            :param jobTempate: The JobTemplate object associated with this job
            :param execParams: The execution paramaters passed into jobTemplate.makerFunction() on Job.Run().

                Reserved execParams keys include: 
                    'job_id'            -> an incremented assigned as a job identifier. Usually assigned by BatchJob
                    'number_of_runs'    -> the number of times the job will run (averaging results)
        """
        self.jobTempate = jobTempate
        self.execParams = execParams
        self.jobResult = None

        # set defaults if they are not already set
        defaults = self.jobTempate.defaults
        for key in defaults:
            if(self.execParams.get(key) == None):
                self.execParams[key] = defaults[key]

    def run(self):
        """
            Runs the job template makerFunction with the set job execParams.
            Raises an exception if attempted to run more than once.

            execParam: "number_of_runs": the number of times this job should be run. The logbook from all the runs will be averaged. If more than one run is used, the JobResult.result will contain a list containing all the individualy returned job results.

            Returns a JobResult which contains a reference to this Job and the results of the run.
        """
        if(self.jobResult != None):
            raise Exception("Cannot run a job more than once.")
        if(self.execParams.get == None
                or self.execParams["number_of_runs"] <= 0):
            raise ValueError("Must run Job zero or more times")

        logbooks = []
        fResults = []

        for i in range(self.execParams["number_of_runs"]):
            resultTuple = self.jobTempate.makerFunction(**self.execParams)
            if(resultTuple == None):
                raise Exception("Template makerFunction must return a tuple of the format (logbook, result)")
            logbook, result = resultTuple
            logbooks.append(logbook)
            fResults.append(result)

        if(len(logbooks) == 1):
            self.jobResult = JobResult(self, logbooks[0], fResults[0])
        else:
            averagedLogbook = LogBookTools.averageLogbookValues(logbooks)
            self.jobResult = JobResult(self, averagedLogbook, fResults)

        return self.jobResult

    def __str__(self):
        s = str(self.jobTempate) + "\n"
        for key in self.execParams:
            s += key + "=" + str(self.execParams[key]) + " \n"
        return s


class JobResult:

    """
        Contains run information about a Job. Returned by Job.run()
        job -> reference to the original job
        logbook -> the Deap.tools.Logbook() object representing the results
        result -> an object containing any extra information needed
    """

    def __init__(self, job, logbook, result):
        self.job = job
        self.logbook = logbook
        self.result = result


class JobCreator:

    """
        Creates a batch of jobs with given paramaters.
    """

    def __init__(self):
        self.staticParams = {}
        self.dynamicParams = {}

    # def useUniqueIds(self, useUnique):
    #     if(len(self.staticParams) > 0 | | len(self.dynamicParams) > 0):
    #         raise Exception("Cannot add unique id's")

    def addRange(self, paramName, **kwargs):
        """
            Adds a range of values to the parameters list
                There are two methods of adding paramaters triggered based on whether 'steps' or 'stepSize' is defined.

                'steps' will create the specified amount of items evenly divided between the start and end. Inclusive of both.
                'stepSize' will add iterations with differences of size 'stepSize'. Inclusive of start and end.

                Examples:
                        1) jobCreator.addRange('mutpx', start=0.1, end=0.4, steps=4)
                                -> will create paramaters with values [0.1, 0.2, 0.3, 0.4]
                        2) jobCreator.addRange('mutpx', start=0.1, end=0.4, stepSize=0.1)
                                -> will create paramaters with values [0.1, 0.2, 0.3, 0.4]
                                TODO:inclusive/exclusive
                Returns the set of paramaters added
        """

        start = kwargs.get('start')
        end = kwargs.get('end')
        steps = kwargs.get('steps')
        stepSize = kwargs.get('stepSize')

        if(start >= end):
            raise ValueError(
                "Paramater \'end\' must be larger than \'start\'")
        if(start == None):
            raise ValueError(
                "Paramater \'start\' must be specified")
        if(end == None):
            raise ValueError(
                "Paramater \'end\' must be specified")

        self.dynamicParams[paramName] = []
        current = start

        if(steps != None):
            # number of steps specified for range
            if(steps - 1 < 0):
                raise ValueError("Paramater \'steps\' must be greater than 1")

            stepSize = (float(end) - start) / (float(steps) - 1)
            for i in range(steps):
                self.dynamicParams[paramName].append(round(current, 13))
                current += stepSize

        elif(stepSize == None):
            raise ValueError(
                "Either \'steps\' or \'stepSize\' must be specified")
        else:  # steps
            while (round(current, 13) <= end):
                # round() removes float inaccuracy
                self.dynamicParams[paramName].append(round(current, 13))
                current += stepSize

        self.__printAddedParams(paramName, self.dynamicParams[paramName])
        self.__confirmSafe()

        return self.dynamicParams[paramName]

    def addSpecific(self, paramName, *args):
        """
            Adds a specific set of values to the evaluation list
                Example:
                jobCreator.addSpecific('mutpx', 0.1, 0.125, 0.3)
                -> will create paramaters with values [0.1, 0.125, 0.3]
        """
        self.dynamicParams[paramName] = []
        for item in args:
            self.dynamicParams[paramName].append(item)

        self.__printAddedParams(paramName, self.dynamicParams[paramName])
        self.__confirmSafe()

        return self.dynamicParams[paramName]

    def addStatic(self, paramName, value):
        """
            Adds a single value to the evaluation list. A static paramater is a paramater that remains the same accross all jobs. Setting values like this will not add to the total number of jobs.
                Calling addStatic() with a paramName the same as an already added one will overwrite the previously added one.
        """
        self.staticParams[paramName] = value

        logging.debug("Added static for paramater " + paramName + ": " + str(self.staticParams[paramName]))
        self.__confirmSafe()

        return self.staticParams[paramName]

    def __printAddedParams(self, paramName, arrayValues):
        if(len(arrayValues) > 10):
            logging.debug("Added values for paramater " + paramName + ": " + "[ Over 10 item ]")
        else:
            logging.debug("Added values for paramater " + paramName + ": " + str(arrayValues))

    def __confirmSafe(self):
        nJobs = self.calcNumJobs()
        if(nJobs > 10000):
            logging.warning("Number of jobs is large(" + str(nJobs) + "). Caution when running batch.")

    def calcNumJobs(self):
        """
            Calulates how many Jobs would be produced if generateJobs() is called
        """
        num = 1
        for item in self.dynamicParams:
            num *= len(self.dynamicParams[item])
        return num

    def generateJobs(self, jobTemplate, addIds=True):
        """ Generates a list of Job objects with paramaters covering all possible combinatins of the given JobCreator paramaters.
            Be careful here as the number of jobs is a factor of all the param counts added. Check calcNumJobs() to see how many jobs would be produced.

                Returns the list of Jobs. The list can be used by a BatchJob instanct to run all teh jobs.
        """
        logging.debug("Generating " + str(self.calcNumJobs()) + " jobs...")

        self.idCounter = 0
        jobs = []
        paramPairStack = []
        keyList = list(self.dynamicParams.keys())

        def recurseParamCombinations(level):
            if(level == len(self.dynamicParams)):
                arguments = {}
                # create the job
                for paramPair in paramPairStack:
                    arguments[paramPair[0]] = paramPair[1]

                for key in self.staticParams:
                    arguments[key] = self.staticParams[key]

                # adds a localy unique id to the job
                if(addIds):
                    if(arguments.get("job_id") == None):
                        arguments["job_id"] = self.idCounter
                        self.idCounter += 1
                    else:
                        raise Exception("\"job_id\" was already used as a paramater. Cannot add unique job id without overwrite. Please use a different name for paramater job paramater \"job_id\"")

                jobs.append(Job(jobTemplate, **arguments))

            else:
                # add to stack and recurse
                paramName = keyList[level]
                for val in self.dynamicParams[paramName]:
                    paramPairStack.append([paramName, val])
                    recurseParamCombinations(level + 1)
                    paramPairStack.pop()

        recurseParamCombinations(0)
        logging.debug("done.")
        return jobs


class BatchJob:

    """
        Runs many jobs concurrently.
    """

    def __init__(self, jobs, processes):
        """
            :param jobs: the list of Job objects to run
            :param processes: the maximum number of Job objects to run concurrently. Integer
        """
        self.jobs = jobs
        self.processes = processes
        self.pool = Pool(processes=self.processes)
        logging.debug("BatchJob created. Processes = " + str(self.processes))

    def run(self):
        """
            Runs all the Job objects concurently on the set number of processes.
            This is a syncronous call.

            Returns a list of JobResult objects returned by the jobs.
        """

        poolInput = self.jobs

        try:
            start_time = time.time()
            results = self.pool.map(_b_runJob, poolInput, chunksize=1)
            end_time = time.time()
            logging.debug("Elapsed time was %g seconds" % (end_time - start_time))
        except KeyboardInterrupt:
            self.terminate()
            self.pool.join()
            print "\nKeyboardInterrupt. Closing all processes"
            sys.exit(0)
        # chunksize=1 makes it so that jobs will be run more in order
        logging.debug("BatchJob finished.")

        return results

    def run_async(self, callback):
        """
            Runs all the Job objects concurently on the set number of processes.
            This is an asyncronous call.
            :param callback: the callback function called when all the Job objects finished running. Prototype:
                def callback(resultList).
                resultList is a list of JobResult objects returned by the jobs.
            :param eachCallback: callback function called after each job is run

            returns the multiprocessing.Pool object used to run the batch. Use this if the ablitity to preemptively terminate the processes is necessary (pool.terminate()). 
        """

        logging.debug("Beginning batch with " + str(len(self.jobs)) + " Job objects.")
        poolInput = self.jobs

        def debugCallback(resultList):
            logging.debug("BatchJob finished")
            callback(resultList)

        aSyncResults = self.pool.map_async(_b_runJob, poolInput, callback=debugCallback, chunksize=1)

    def run_async_ind(self, eachCallback):
        """
            Runs all the Job objects concurently on the set number of processes. This is an asyncronous call that allows the results to be returned one by one.
            :param eachCallback: callback function called after each job is run. Format: eachCallback(jobResult), where jobResult is the returned JobResult object

            returns nothing
        """

        logging.debug("Beginning batch with " + str(len(self.jobs)) + " Job objects.")
        poolInput = self.jobs

        aSyncResults = self.pool.imap(_b_runJob, poolInput, chunksize=1)

        print aSyncResults
        if eachCallback != None:
            while True:
                try:
                    jobResult = aSyncResults.next()
                    eachCallback(jobResult)
                except StopIteration:
                    break

    def terminate(self):
        self.pool.terminate()


def _b_runJob(job):
    """
        Private. This is a picklable function used to run a specified Job

    """
    try:
        logging.debug("Running: " + str(job.execParams.get("job_id", "no job_id found")))
        jobResult = job.run()
        return jobResult
    except KeyboardInterrupt:
        raise KeyboardInterruptError()


class KeyboardInterruptError(Exception):

    """
    # Empty keyboard interrupt error is required for BatchJob multiprocessing interuptions. For some reason python does not handle regular KeyboardInterrupt as expected.
    """
    pass
