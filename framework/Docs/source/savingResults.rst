Saving Results
--------------------


.. code-block:: py

    from deap import tools
    from Batch import job
    import logging

    # enable logging
    logging.basicConfig(level=logging.DEBUG)

    # define the maker function


    def someJobFunction(**params):
        print "The values are " + str(params['foo']) + " " + str(params['bar'])

        logbook = tools.Logbook()
        # ... populate logbook

        return (logbook, None)


    logging.basicConfig(level=logging.DEBUG)

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

    The values are 0.0 0.0
    The values are 0.0 0.2
    The values are 0.0 0.4
    The values are 0.0 0.6
    The values are 0.0 0.8
    The values are 0.0 1.0
    The values are 1.0 0.0
    The values are 1.0 0.2
    The values are 1.0 0.4
    The values are 1.0 0.6
    The values are 1.0 0.8
    The values are 1.0 1.0
    Single job logbook:
                                       result  
                                    -----------
    bar foo job_id  number_of_runs  bar foo
    0   0   0       1               0   0  
    Super Logbook:
                                       result  
                                    -----------
    bar foo job_id  number_of_runs  bar foo
    0   0   0       1               0   0  
    0.2 0   1       1               0.2 0  
    0.4 0   2       1               0.4 0  
    0.6 0   3       1               0.6 0  
    0.8 0   4       1               0.8 0  
    1   0   5       1               1   0  
    0   1   6       1               0   1  
    0.2 1   7       1               0.2 1  
    0.4 1   8       1               0.4 1  
    0.6 1   9       1               0.6 1  
    0.8 1   10      1               0.8 1  
    1   1   11      1               1   1  
    Loaded pickle single logbook:
                                       result  
                                    -----------
    bar foo job_id  number_of_runs  bar foo
    0   0   0       1               0   0  
    Loaded csv single logbook:
    {'bar': ['0.0'], 'job_id': ['0'], 'result_bar': ['0.0'], 'number_of_runs': ['1'], 'foo': ['0.0'], 'result_foo': ['0.0']}
    Loaded pickle super logbook:
                                       result  
                                    -----------
    bar foo job_id  number_of_runs  bar foo
    0   0   0       1               0   0  
    0.2 0   1       1               0.2 0  
    0.4 0   2       1               0.4 0  
    0.6 0   3       1               0.6 0  
    0.8 0   4       1               0.8 0  
    1   0   5       1               1   0  
    0   1   6       1               0   1  
    0.2 1   7       1               0.2 1  
    0.4 1   8       1               0.4 1  
    0.6 1   9       1               0.6 1  
    0.8 1   10      1               0.8 1  
    1   1   11      1               1   1  
    Loaded csv super logbook:
    {'number_of_runs': ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1'], 'job_id': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'], 'result_bar': ['0.0', '0.2', '0.4', '0.6', '0.8', '1.0', '0.0', '0.2', '0.4', '0.6', '0.8', '1.0'], 'bar': ['0.0', '0.2', '0.4', '0.6', '0.8', '1.0', '0.0', '0.2', '0.4', '0.6', '0.8', '1.0'], 'foo': ['0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '1.0', '1.0', '1.0', '1.0', '1.0', '1.0'], 'result_foo': ['0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '1.0', '1.0', '1.0', '1.0', '1.0', '1.0']}
