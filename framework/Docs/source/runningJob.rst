Running a Job
--------------------

A Job is a container for a set of execution paramaters to be used with a JobTemplate. A Job can only be run once. Used by BatchJob to execute multiple Jobs concurrently.

Each Job created must have an associated JobTemplate object. A JobTemplate is a wrapper for a given delegate function named the makerFunction. When run by a job, the makerfunction is called with the jobs specific execParams as paramaters.

The makerfunction must follow the following prototype: 

.. code-block:: py

    def someJobFunction(**params):
        ...
        return (logbook, results)


For Deap compatability, the output of the makerfunction is a tuple containing a deap.tools.Logbook() object as the first entry and any object as the second entry. The logbook is later used by tools in the display and results modules and should be not-null. The results object can be set as any result values that are needed after the job is complete. Results can be null.

Important:
    - The makerFunction must be picklable if it is to be used by BatchJob.
    - Defining the makerFunction in the global scope will usually ensure it is picklable (unless it has some wierd references).

The params argument of the function is a user defined set of paramaters that will be provided at run time. This allows one JobTemplate object to be used with many Job objects.

Sample code for running a single job:

.. code-block:: py

    import logging
    from deap import tools
    from Batch import job

    #enable logging
    logging.basicConfig(level=logging.DEBUG) 

    #define the maker function
    def someJobFunction(**params):
        print "The value is " + str(params['value'])

        logbook = tools.Logbook() 
        # ... populate logbook

        return (logbook, None)


    template = job.JobTemplate(someJobFunction)
    template.setDefaults(value=0)

    ajob = job.Job(template)
    ajob.run()

    ajob2 = job.Job(template, value=3)
    ajob2.run()


Yields the following output:

.. code-block:: bash

    The value is 0
    The value is 3

Note that the default value that was set with JobTemplate.setDefaults() is overriden in the aJob2.