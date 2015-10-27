Running Many Jobs
--------------------

.. code-block:: py

    from deap import tools
    from Batch import job
    import logging

    # enable logging
    logging.basicConfig(level=logging.DEBUG)

    def someJobFunction(**params):
        print "The values are " + str(params['foo']) + " " + str(params['bar'])

        logbook = tools.Logbook()
        # ... populate logbook

        return (logbook, None)


    template = job.JobTemplate(someJobFunction)
    template.setDefaults(foo=3, bar=4)

    jobCreator = job.JobCreator()
    jobCreator.addRange('foo', start=0.0, end=1.0, steps=2)
    jobCreator.addRange('bar', start=0.0, end=1.0, stepSize=0.2)

    # all other params will take defaults
    jobs = jobCreator.generateJobs(template)

    batchJob = job.BatchJob(jobs, 2)
    results = batchJob.run()


Yields the following terminal output:

.. code-block:: py

    DEBUG:root:Added values for paramater foo: [0.0, 1.0]
    DEBUG:root:Added values for paramater bar: [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    DEBUG:root:Generating 12 jobs...
    DEBUG:root:done.
    DEBUG:root:BatchJob created. Processes = 2
    DEBUG:root:Running: 0
    DEBUG:root:Running: 1
    The values are 0.0 0.0
    The values are 0.0 0.2
    DEBUG:root:Running: 2
    The values are 0.0 0.4
    DEBUG:root:Running: 3
    The values are 0.0 0.6
    DEBUG:root:Running: 4
    The values are 0.0 0.8
    DEBUG:root:Running: 5
    The values are 0.0 1.0
    DEBUG:root:Running: 6
    The values are 1.0 0.0
    DEBUG:root:Running: 7
    The values are 1.0 0.2
    DEBUG:root:Running: 8
    The values are 1.0 0.4
    DEBUG:root:Running: 9
    The values are 1.0 0.6
    DEBUG:root:Running: 10
    The values are 1.0 0.8
    DEBUG:root:Running: 11
    The values are 1.0 1.0
    DEBUG:root:Elapsed time was 0.00263786 seconds
    DEBUG:root:BatchJob finished.
