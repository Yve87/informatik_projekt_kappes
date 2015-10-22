Run Jobs with Database Persistance
--------------------


The jobs run in this example are continously saved to the provided MySQL database as they complete.
This example uses the maker function defined in `Example GA-simple maker function <./_static/runGaSimpleMakerFunction.py>`_.


.. code-block:: py

    import logging
    from Batch import job
    from Batch import results

    logging.basicConfig(level=logging.DEBUG)

    template = job.JobTemplate(runGASimple)
    template.setDefaults(indpb=0.8, tournsize=20, popSize=20, cxpb=0.5, mutpb=0.5, ngen=10, number_of_runs=1, verbose=False)

    jobCreator = job.JobCreator()
    jobCreator.addRange('cxpb', start=0.0, end=1.0, stepSize=0.3)
    jobCreator.addRange('mutpb', start=0.0, end=1.0, stepSize=0.3)
    # all other params will take defaults
    jobs = jobCreator.generateJobs(template)

    batchJob = job.BatchJob(jobs, 2)

    dbh = results.DatabaseResults('localhost', 'damian', 'damian', 'DeapBatch', 'demoTable')

    dbh.persistRun(batchJob)




.. code-block:: py

    DEBUG:root:Added values for paramater cxpb: [0.0, 0.3, 0.6, 0.9]
    DEBUG:root:Added values for paramater mutpb: [0.0, 0.3, 0.6, 0.9]
    DEBUG:root:Generating 16 jobs...
    DEBUG:root:done.
    DEBUG:root:BatchJob created. Processes = 2
    DEBUG:root:Beginning batch with 16 Job objects.
    <multiprocessing.pool.IMapIterator object at 0x7f20c3e128d0>
    DEBUG:root:Running: 1
    DEBUG:root:Running: 0
    runWithDatabasePersistance.py:23: RuntimeWarning: Could not add vertex ids, there is already an 'id' vertex attribute at foreign-graphml.c:443
      NETWORK = igraph.Graph.Read_GraphML("./graph_nren_rand.graphml")  # Ignore produced warning
    runWithDatabasePersistance.py:23: RuntimeWarning: Could not add vertex ids, there is already an 'id' vertex attribute at foreign-graphml.c:443
      NETWORK = igraph.Graph.Read_GraphML("./graph_nren_rand.graphml")  # Ignore produced warning
    DEBUG:root:Running: 2
    DEBUG:root:CREATE TABLE demoTable(iID INT PRIMARY KEY AUTO_INCREMENT,result_avg FLOAT,indpb FLOAT,verbose INTEGER,result_max FLOAT,result_nevals INTEGER,result_gen INTEGER,result_std FLOAT,ngen INTEGER,popSize INTEGER,cxpb FLOAT,result_median FLOAT,tournsize INTEGER,result_min FLOAT,number_of_runs INTEGER,mutpb FLOAT,job_id INTEGER)
    DEBUG:root:Running: 3
    DEBUG:root:INSERT INTO demoTable (iId,result_avg,indpb,verbose,result_max,result_nevals,result_gen,result_std,n
    DEBUG:root:INSERT INTO demoTable (iId,result_avg,indpb,verbose,result_max,result_nevals,result_gen,result_std,n
    DEBUG:root:Running: 4
    DEBUG:root:INSERT INTO demoTable (iId,result_avg,indpb,verbose,result_max,result_nevals,result_gen,result_std,n
    DEBUG:root:Running: 5
    DEBUG:root:INSERT INTO demoTable (iId,result_avg,indpb,verbose,result_max,result_nevals,result_gen,result_std,n
    DEBUG:root:Running: 6
    DEBUG:root:INSERT INTO demoTable (iId,result_avg,indpb,verbose,result_max,result_nevals,result_gen,result_std,n
    DEBUG:root:Running: 7
    DEBUG:root:INSERT INTO demoTable (iId,result_avg,indpb,verbose,result_max,result_nevals,result_gen,result_std,n
    DEBUG:root:Running: 8
    DEBUG:root:INSERT INTO demoTable (iId,result_avg,indpb,verbose,result_max,result_nevals,result_gen,result_std,n
    DEBUG:root:Running: 9
    DEBUG:root:INSERT INTO demoTable (iId,result_avg,indpb,verbose,result_max,result_nevals,result_gen,result_std,n
    DEBUG:root:Running: 10
    DEBUG:root:INSERT INTO demoTable (iId,result_avg,indpb,verbose,result_max,result_nevals,result_gen,result_std,n
    DEBUG:root:Running: 11
    DEBUG:root:INSERT INTO demoTable (iId,result_avg,indpb,verbose,result_max,result_nevals,result_gen,result_std,n
    DEBUG:root:Running: 12
    DEBUG:root:INSERT INTO demoTable (iId,result_avg,indpb,verbose,result_max,result_nevals,result_gen,result_std,n
    DEBUG:root:Running: 13
    DEBUG:root:INSERT INTO demoTable (iId,result_avg,indpb,verbose,result_max,result_nevals,result_gen,result_std,n
    DEBUG:root:Running: 14
    DEBUG:root:INSERT INTO demoTable (iId,result_avg,indpb,verbose,result_max,result_nevals,result_gen,result_std,n
    DEBUG:root:Running: 15
    DEBUG:root:INSERT INTO demoTable (iId,result_avg,indpb,verbose,result_max,result_nevals,result_gen,result_std,n
    DEBUG:root:INSERT INTO demoTable (iId,result_avg,indpb,verbose,result_max,result_nevals,result_gen,result_std,n
    DEBUG:root:INSERT INTO demoTable (iId,result_avg,indpb,verbose,result_max,result_nevals,result_gen,result_std,n
