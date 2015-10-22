.. DeapBatch documentation master file, created by
   sphinx-quickstart on Mon Aug  3 12:57:22 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to DeapBatch's documentation!
=====================================

Tutorial:

.. toctree::
    :maxdepth: 3

    Running a job. <runningJob>
    Running many jobs. <runningManyJobs>
    Saving Results. <savingResults>
    Run Jobs with Database Persistance <runWithDatabasePersistance>
    Plot with Templates <plotWithTemplates>
    Real Time Update With Externaly Rrunning BatchJob <realTimeGraph.rst>


:download: `Example GA-simple maker function <./_static/runGaSimpleMakerFunction.py>`_


Modules:

.. toctree::
    :maxdepth: 3

    job <job>
    results <results>
    display <display>

Classes:

.. hlist::
    * :py:class:`job.JobTemplate`
    * :py:class:`job.Job`
    * :py:class:`job.BatchJob`
    * :py:class:`job.JobCreator`
    * :py:class:`job.JobResult`


.. hlist::
    * :py:class:`results.DatabaseResults`
    * :py:class:`results.Filter`
    * :py:class:`results.LogBookTools`
    * :py:class:`results.Util`
    * :py:class:`results.DatabaseResults`


.. hlist::
    * :py:class:`display.Plotter`
    * :py:class:`display.Plotter.Templates`

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

