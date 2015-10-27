import igraph
import random
import sys
import numpy as np
from scoop import futures
from deap import creator, base, tools, algorithms


"""
Definition of the genetic algorithm
using the DeapBatch framework
"""

def runGASimple(**kwargs):

    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)

    # registering stat will mean it will record it for every individual (or group of individuals)
    stats1 = tools.Statistics(key=lambda ind: ind.fitness.values)
    stats1.register("min", np.min)
    stats1.register("avg", np.mean)
    stats1.register("max", np.max)
    stats1.register("median", np.median)
    stats1.register("std", np.std)

    # load the graph from the given argument path (.graphml file)
    NETWORK = igraph.Graph.Read_GraphML("./graph_nren_rand.graphml")  # Ignore produced warning
    if "weight" not in NETWORK.es.attributes():
        print("no weighting given, assuming '1'")
        NETWORK.es["weight"] = 1

    def monitorFitness(ind, verbose=False):
        fit = np.sum(ind)
        if verbose:
            net = NETWORK
            covered = 0
            uncovered = 0
            for edge in net.es():
                if not ind[edge.tuple[0]] and not ind[edge.tuple[1]]:
                    uncovered += 1
                else:
                    covered += 1
            print "|V| = {}; |E| = {}; monitors = {}; covered = {}; uncovered = {}".format(net.vcount(), net.ecount(), fit, covered, uncovered)
        fit += uncoveredEdgePenalty(ind, verbose)
        return fit,

    def uncoveredEdgePenalty(ind, verbose=False):
        g = NETWORK
        penalty = 0
        for edge in g.es():
            if not ind[edge.tuple[0]] and not ind[edge.tuple[1]]:
                if verbose:
                    print "penalty for edge {}: v{} -> v{} = {}".format(edge.index, edge.tuple[0], edge.tuple[1], edge["weight"])
                penalty += 2 * int(edge["weight"])
        return penalty

    toolbox = base.Toolbox()
    #toolbox.register("map", futures.map)
    toolbox.register("attr_bool", np.random.randint, 2)
    toolbox.register("individual", tools.initRepeat,
                     creator.Individual, toolbox.attr_bool, n=NETWORK.vcount())
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    FITNESS = monitorFitness
    toolbox.register("evaluate", FITNESS)

    toolbox.register("mate", tools.cxOnePoint)
    toolbox.register("mutate", tools.mutFlipBit, indpb=kwargs["indpb"])
    toolbox.register("select", tools.selTournament, tournsize=kwargs["tournsize"])

    pop, logbook = algorithms.eaSimple(toolbox.population(
        n=kwargs["popSize"]), toolbox, cxpb=kwargs["cxpb"], mutpb=kwargs["mutpb"], ngen=kwargs["ngen"], verbose=kwargs["verbose"], stats=stats1)

    return (logbook, None)

"""
Steps performed in the following demo:
1) Running a GA
2) Running Multiple GA's with paramaters
3) Saving results to CSV, or pickle object
4) Opening results from CSV, picklable
5) Saving DB Results
"""

import logging
from Batch import job
from Batch import results
from Batch import display
from Batch import util
from pylab import *
import time


def demo1(indpb, tournsize, popsize, cxpb, mutpb, ngen, number_of_runs, verbose):
    #single GA job
    logging.basicConfig(level=logging.DEBUG)

    template = job.JobTemplate(runGASimple)
    #template.setDefaults(indpb=0.8, tournsize=20, popSize=20, cxpb=0.5, mutpb=0.5, ngen=20, number_of_runs=1, verbose=True)
    template.setDefaults(indpb=indpb, tournsize=tournsize, popSize=popsize, cxpb=cxpb, mutpb=mutpb, ngen=ngen, number_of_runs=number_of_runs, verbose=verbose)

    ajob = job.Job(template)
    ajob.run()

    pass

def demo2():
    # RUN BATCH JOB
    logging.basicConfig(level=logging.DEBUG)

    template = job.JobTemplate(runGASimple)
    template.setDefaults(indpb=0.8, tournsize=20, popSize=20, cxpb=0.5, mutpb=0.5, ngen=20, number_of_runs=1, verbose=False)

    jobCreator = job.JobCreator()
    jobCreator.addRange('cxpb', start=0.0, end=1.0, stepSize=0.3)
    jobCreator.addRange('mutpb', start=0.0, end=1.0, stepSize=0.3)

    # all other params will take defaults
    jobs = jobCreator.generateJobs(template)

    batchJob = job.BatchJob(jobs, 5)
    results = batchJob.run()
    pass

def demo3():
    # SAVE RESULT TO PICKLE
    logging.basicConfig(level=logging.DEBUG)

    template = job.JobTemplate(runGASimple)
    template.setDefaults(indpb=0.8, tournsize=20, popSize=20, cxpb=0.5, mutpb=0.5, ngen=20, number_of_runs=2, verbose=False)

    ajob = job.Job(template)
    jobResult = ajob.run()

    print jobResult.logbook

    util.saveLogbook("demoLogbook.lgb", results.LogBookTools.createLogbookFrom(jobResult))
    util.saveCSV("demoLogbook.csv", jobResult.logbook)

    pass

def demo4():
    # Load saved results

    print util.loadLogbook("demoLogbook.lgb")

    pass

def demo5():
    # Running a GA with Database
    logging.basicConfig(level=logging.DEBUG)

    template = job.JobTemplate(runGASimple)
    template.setDefaults(indpb=0.8, tournsize=20, popSize=20, cxpb=0.5, mutpb=0.5, ngen=10, number_of_runs=1, verbose=False)

    jobCreator = job.JobCreator()
    jobCreator.addRange('cxpb', start=0.0, end=1.0, stepSize=0.1)
    jobCreator.addRange('mutpb', start=0.0, end=1.0, stepSize=0.1)
    # all other params will take defaults
    jobs = jobCreator.generateJobs(template)

    batchJob = job.BatchJob(jobs, 5)

    # Change database entries
    DBUSER = 'changeme'
    DBPASS = 'changeme'
    DBHOST = 'changeme'
    DB = 'changeme'
    TABLE = 'changeme'

    dbh = results.DatabaseResults(DBHOST, DBUSER, DBPASS, DB, TABLE)

    def update(jr):
        print 'Writing to database...'

    dbh.persistRun(batchJob, callback=update)

    pass

if (__name__ == "__main__"):
    demoNumber = sys.argv[1:][0]
#Parameter über sys.argv eingeben statt über raw_input!
    if(demoNumber == "1"):
        #indpb=0.8, tournsize=20, popSize=20, cxpb=0.5, mutpb=0.5, ngen=20, number_of_runs=1, verbose=True)
        indpb = float(raw_input("Probability for each attribute to be mutated (float): "))
        tournsize = long(raw_input("Number of individuals participating in each tournament: "))
        popSize = long(raw_input("Population size: "))
        cxpb = float(raw_input("Probability that an offspring is produced by crossover: "))
        mutpb = float (raw_input("Probability that an offspring is produced by mutation: "))
        ngen = long(raw_input("Number of generations: "))
        number_of_runs = long(raw_input("Number of Runs: "))
        verbosee = bool(raw_input("Verbose output (Boolean): "))

        demo1(indpb,tournsize,popSize,cxpb,mutpb,ngen,number_of_runs,verbosee)


    elif(demoNumber == "2"):
        demo2()
    elif(demoNumber == "3"):
        demo3()
    elif(demoNumber == "4"):
        demo4()
    elif(demoNumber == "5"):
        demo5()
