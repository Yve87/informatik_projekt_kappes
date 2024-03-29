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

def demo2(indpb, tournsize, popsize, cxpb, mutpb, ngen, number_of_runs, verbose,cxpb_start,cxpb_end, cxpb_stepSize, mutpb_start, mutpb_end, mutpb_stepSize, specific_type, specific_param1,specific_param2,specific_param3,specific_param4,specific_param5):
    # RUN BATCH JOB
    logging.basicConfig(level=logging.DEBUG)

    template = job.JobTemplate(runGASimple)
    #template.setDefaults(indpb=0.8, tournsize=20, popSize=20, cxpb=0.5, mutpb=0.5, ngen=20, number_of_runs=1, verbose=False)
    template.setDefaults(indpb=indpb, tournsize=tournsize, popSize=popsize, cxpb=cxpb, mutpb=mutpb, ngen=ngen, number_of_runs=number_of_runs, verbose=verbose)


    jobCreator = job.JobCreator()
    #range OR specific
    jobCreator.addRange('cxpb', start=cxpb_start, end=cxpb_end, stepSize=cxpb_stepSize)
    jobCreator.addRange('mutpb', start=mutpb_start, end=mutpb_end, stepSize=mutpb_stepSize)
    jobCreator.addSpecific(specific_type,specific_param1,specific_param2,specific_param3,specific_param4,specific_param5)

    # all other params will take defaults
    jobs = jobCreator.generateJobs(template)

    batchJob = job.BatchJob(jobs, 5)
    results = batchJob.run()
    pass

def demo3(indpb, tournsize, popsize, cxpb, mutpb, ngen, number_of_runs, verbose, logbook_lgb_filename, logbook_csv_filename):
    # SAVE RESULT TO PICKLE
    logging.basicConfig(level=logging.DEBUG)

    template = job.JobTemplate(runGASimple)
    #template.setDefaults(indpb=0.8, tournsize=20, popSize=20, cxpb=0.5, mutpb=0.5, ngen=20, number_of_runs=2, verbose=False)
    template.setDefaults(indpb=indpb, tournsize=tournsize, popSize=popsize, cxpb=cxpb, mutpb=mutpb, ngen=ngen, number_of_runs=number_of_runs, verbose=verbose)

    ajob = job.Job(template)
    jobResult = ajob.run()

    print jobResult.logbook

    util.saveLogbook(logbook_lgb_filename, results.LogBookTools.createLogbookFrom(jobResult))
    util.saveCSV(logbook_csv_filename, jobResult.logbook)

    pass

def demo4(filename):
    # Load saved results

    print util.loadLogbook(filename)

    pass

def demo5(DBUSER, DBPASS, DBHOST, DB, TABLE, indpb, tournsize, popsize, cxpb, mutpb, ngen, number_of_runs, verbose, cxpb_start,cxpb_end, cxpb_stepSize, mutpb_start, mutpb_end, mutpb_stepSize, batch_amount):
    # Running a GA with Database
    logging.basicConfig(level=logging.DEBUG)

    template = job.JobTemplate(runGASimple)
    #template.setDefaults(indpb=0.8, tournsize=20, popSize=20, cxpb=0.5, mutpb=0.5, ngen=10, number_of_runs=1, verbose=False)
    template.setDefaults(indpb=indpb, tournsize=tournsize, popSize=popsize, cxpb=cxpb, mutpb=mutpb, ngen=ngen, number_of_runs=number_of_runs, verbose=verbose)

    jobCreator = job.JobCreator()
    jobCreator.addRange('cxpb', start=cxpb_start, end=cxpb_end, stepSize=cxpb_stepSize)
    jobCreator.addRange('mutpb', start=mutpb_start, end=mutpb_end, stepSize=mutpb_stepSize)
    # all other params will take defaults
    jobs = jobCreator.generateJobs(template)

    batchJob = job.BatchJob(jobs, batch_amount)

    dbh = results.DatabaseResults(DBHOST, DBUSER, DBPASS, DB, TABLE)

    def update(jr):
        print 'Writing to database...'

    dbh.persistRun(batchJob, callback=update)

    pass


import json
import os.path
import getopt;

if (__name__ == "__main__"):
    #sys.argv[1:] returns a list (array) of arguments

    if not sys.argv[1:]:
        print("Run with -h param for help")
    else:
        arg1 = sys.argv[1:][0]
        if (arg1== "-h"):
            try:
                if sys.argv[1:][1] == "-singleJob":
                      print("indpb = Probability for each attribute to be mutated")
                      print("tournsize = Number of individuals participating in each tournament")
                      print("popSize = Population size")
                      print("cxpb = Probability that an offspring is produced by crossover")
                      print("mutpb = Probability that an offspring is produced by mutation")
                      print("ngen = Number of generations")
                      print("number_of_runs = Number of Runs")
                      print("verbosee = Verbose output (Boolean)")
                elif sys.argv[1:][1] == "-batchJob":
                      print("indpb = Probability for each attribute to be mutated")
                      print("tournsize = Number of individuals participating in each tournament")
                      print("popSize = Population size")
                      print("cxpb = Probability that an offspring is produced by crossover")
                      print("mutpb = Probability that an offspring is produced by mutation")
                      print("ngen = Number of generations")
                      print("number_of_runs = Number of Runs")
                      print("verbosee = Verbose output (Boolean)")
                elif sys.argv[1:][1] == "-savePickle":
                    print("indpb = Probability for each attribute to be mutated")
                    print("tournsize = Number of individuals participating in each tournament")
                    print("popSize = Population size")
                    print("cxpb = Probability that an offspring is produced by crossover")
                    print("mutpb = Probability that an offspring is produced by mutation")
                    print("ngen = Number of generations")
                    print("number_of_runs = Number of Runs")
                    print("verbosee = Verbose output (Boolean)")
                elif sys.argv[1:][1] == "-load":
                    print("no extra params")
                elif sys.argv[1:][1] == "-runWithDB":
                    print("indpb = Probability for each attribute to be mutated")
                    print("tournsize = Number of individuals participating in each tournament")
                    print("popSize = Population size")
                    print("cxpb = Probability that an offspring is produced by crossover")
                    print("mutpb = Probability that an offspring is produced by mutation")
                    print("ngen = Number of generations")
                    print("number_of_runs = Number of Runs")
                    print("verbosee = Verbose output (Boolean)")
                elif sys.argv[1:][1] == "-cfgDB":
                    print("no extra params")
                else:
                    raise IndexError()
            except:
                print("-h -X:")
                print("-singleJob: single GA job")
                print("-batchJob: Run batch job")
                print("-savePickle: save results to pickle")
                print("-load: load saved results")
                print("-runWithDB: running ga with database")
                print("-cfgDB: set db config")
        elif(arg1 == "-cfgDB"):
            DBUSER = raw_input("DB User: ")
            DBPASS = raw_input("DB User Password: ")
            DBHOST = raw_input("DB Host: ")
            DB = raw_input("DB Name: ")
            TABLE = raw_input("Table name: ")
            config = {'DBUSER': DBUSER, 'DBPASS': DBPASS,'DBHOST': DBHOST,'DB': DB,'TABLE': TABLE}
            with open('config.json', 'w') as f:
                    json.dump(config, f)

        elif(arg1 == "-singleJob"):
            if(len(sys.argv[1:]) < 8):
                print("Missing Parameter. Required input: -singleJob indpd tournsize popsize cxpb mutpb ngen number_of_runs verbose(boolean)")
            else:
                demo1(float(sys.argv[1:][1]),
                long(sys.argv[1:][2]),
                long(sys.argv[1:][3]),
                float(sys.argv[1:][4]),
                float(sys.argv[1:][5]),
                long(sys.argv[1:][6]),
                long(sys.argv[1:][7]),
                bool(sys.argv[1:][8]))


        elif(arg1 == "-batchJob"):
            if(len(sys.argv[1:])<8):
                print("Missing Parameter. Required input: -batchJob indpd tournsize popsize cxpb mutpb ngen number_of_runs verbose(boolean) cxpb_start cxpb_end cxpb_stepSize mutpb_start mutpb_end mutpb_stepSize specific_type specific_param1 specific_param2 specific_param3 specific_param4 specific_param5")
            else:
                    demo2(float(sys.argv[1:][1]),
                    long(sys.argv[1:][2]),
                    long(sys.argv[1:][3]),
                    float(sys.argv[1:][4]),
                    float(sys.argv[1:][5]),
                    long(sys.argv[1:][6]),
                    long(sys.argv[1:][7]),
                    bool(sys.argv[1:][8]),
                    long(sys.argv[1:][9]),
                    long(sys.argv[1:][10]),
                    long(sys.argv[1:][11]),
                    long(sys.argv[1:][12]),
                    long(sys.argv[1:][13]),
                    long(sys.argv[1:][14]),
                    sys.argv[1:][15],
                    long(sys.argv[1:][16]),
                    long(sys.argv[1:][17]),
                    long(sys.argv[1:][18]),
                    long(sys.argv[1:][19]),
                    long(sys.argv[1:][20]))

        elif(arg1 == "-savePickle"):
            if(len(sys.argv[1:])<8):
                print("Missing Parameter. Required input: -savePickle indpd tournsize popsize cxpb mutpb ngen number_of_runs verbose(boolean) logbook_filename(.lgb file) logbook_filename(.csv file)")
            else:
                    demo3(float(sys.argv[1:][1]),
                    long(sys.argv[1:][2]),
                    long(sys.argv[1:][3]),
                    float(sys.argv[1:][4]),
                    float(sys.argv[1:][5]),
                    long(sys.argv[1:][6]),
                    long(sys.argv[1:][7]),
                    bool(sys.argv[1:][8]),
                    sys.argv[1:][9],
                    sys.argv[1:][10])

        elif(arg1 == "-load"):
            if(len(sys.argv[1:])<2):
                print("Missing Parameter. Required input: -load filename")
            else:
                demo4(sys.argv[1:][1])

        elif(arg1 == "-runWithDB"):
            if(len(sys.argv[1:])<8):
                print("Missing Parameter. Required input: -withWithDB indpd tournsize popsize cxpb mutpb ngen number_of_runs verbose(boolean)")
            else:
                if(os.path.isfile("config.json")):
                    with open('config.json', 'r') as f:
                        config = json.load(f)
                        demo5(
                        config["DBUSER"],
                        config["DBPASS"],
                        config["DBHOST"],
                        config["DB"],
                        config["TABLE"],
                        float(sys.argv[1:][1]),
                        long(sys.argv[1:][2]),
                        long(sys.argv[1:][3]),
                        float(sys.argv[1:][4]),
                        float(sys.argv[1:][5]),
                        long(sys.argv[1:][6]),
                        long(sys.argv[1:][7]),
                        bool(sys.argv[1:][8]))
                else:
                    print("No config file. Run -cfgDB first")
#closures
