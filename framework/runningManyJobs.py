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
