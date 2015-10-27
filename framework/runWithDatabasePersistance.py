import igraph
import random
import sys
import numpy as np
from scoop import futures
from deap import creator, base, tools, algorithms


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


import logging
from Batch import job
from Batch import results
from Batch import display

logging.basicConfig(level=logging.DEBUG)

dbh = results.DatabaseResults('localhost', 'damian', 'damian', 'DeapBatch', 'demoTable')

filter = results.Filter(dbh, job_id=10)
display.Plotter.Templates.plot_2D_Fit_vs_Gen_MinMaxAvg(filter, show=True)

filter = results.Filter(dbh, cxpb=0.3)  # must have data which matches cxpb = 0.3!
display.Plotter.Templates.plot_2D_Fit_vs_Gen__MultiMutpb(filter, everyNth=3, show=True)

filter = results.Filter(dbh)
display.Plotter.Templates.plot_3D_Mutpb_Cxpb(filter, useGeneration=10, show=True)

# logging.basicConfig(level=logging.DEBUG)

# template = job.JobTemplate(runGASimple)
# template.setDefaults(indpb=0.8, tournsize=20, popSize=20, cxpb=0.5, mutpb=0.5, ngen=10, number_of_runs=1, verbose=False)

# jobCreator = job.JobCreator()
# jobCreator.addRange('cxpb', start=0.0, end=1.0, stepSize=0.1)
# jobCreator.addRange('mutpb', start=0.0, end=1.0, stepSize=0.1)
# #all other params will take defaults
# jobs = jobCreator.generateJobs(template)

# batchJob = job.BatchJob(jobs, 2)


# dbh = results.DatabaseResults('localhost', 'damian', 'damian', 'DeapBatch', 'demoTable')

# def update(jr):
#     if(update.count > 10):
#         update.plotter.clearAx()
#         filter = results.Filter(update.dbh, "mutpb", "cxpb", "result_avg", result_gen=10)
#         update.plotter.plot_3D(filter, xAxis="mutpb", yAxis="cxpb", zAxis="result_avg")
#         update.plotter.setGrid(False)
#         update.plotter.draw()
#     update.count += 1

# update.count = 0
# update.plotter = display.Plotter(isIon=True)
# update.dbh = dbh
# dbh.persistRun(batchJob, callback=update)

# update.plotter.show()
