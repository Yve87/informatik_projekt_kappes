from deap import tools
from Batch import job
import logging

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
