from deap import tools
from Batch import job
from Batch import results
import logging

# logging.basicConfig(level=logging.DEBUG)

def someJobFunction(**params):
    print "The values are " + str(params['foo']) + " " + str(params['bar'])

    logbook = tools.Logbook()
    logbook.record(foo=params['foo'], bar=params['bar'])

    return (logbook, None)


template = job.JobTemplate(someJobFunction)
template.setDefaults(foo=3, bar=4)

jobCreator = job.JobCreator()
jobCreator.addRange('foo', start=0.0, end=1.0, steps=2)
jobCreator.addRange('bar', start=0.0, end=1.0, stepSize=0.2)

# all other params will take defaults
jobs = jobCreator.generateJobs(template)

batchJob = job.BatchJob(jobs, 2)
res = batchJob.run()


singleResult = res[0]

# create a logbook from the JobResult. Will append the Job info to each line of the JobReslt.logbook
jobLogbook = results.LogBookTools.createLogbookFrom(singleResult)
print "Single job logbook:"
print jobLogbook

# save
results.Util.saveLogbook("singleJob.lgb", jobLogbook)
results.Util.saveCSV("singleJob.csv", jobLogbook)


# Create a super logbook from all of the JobResult objects. Can be saved and later used with the Filter() object to refine or plot results.
superBook = results.LogBookTools.createSuperLogbook(res)
print "Super Logbook:"
print superBook
# save
results.Util.saveLogbook("allJobs.lgb", superBook)
results.Util.saveCSV("allJobs.csv", superBook)


print "Loaded pickle single logbook:"
print results.Util.loadLogbook("singleJob.lgb")
print "Loaded csv single logbook:"
print results.Util.loadCSV("singleJob.csv")

print "Loaded pickle super logbook:"
print results.Util.loadLogbook("allJobs.lgb")
print "Loaded csv super logbook:"
print results.Util.loadCSV("allJobs.csv")
