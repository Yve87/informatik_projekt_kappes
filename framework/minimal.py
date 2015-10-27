import igraph
import random
import sys
import numpy as np
from scoop import futures

from deap import creator, base, tools, algorithms


def createRealLogBook():

    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)


    # registering stat will mean it will record it for every individual (or group of individuals)
    stats1 = tools.Statistics(key=lambda ind: ind.fitness.values)
    stats1.register("min", np.min)
    stats1.register("avg", np.mean)
    stats1.register("max", np.max)

    stats2 = tools.Statistics(key=len)
    stats2.register("amount", np.mean)

    stats = tools.MultiStatistics(fitness=stats1, size=stats2)


    # load the graph from the given argument path (.graphml file)
    if len(sys.argv) > 1:
        NETWORK = igraph.Graph.Read_GraphML(sys.argv[1])  # Ignore produced warning
        if "weight" not in NETWORK.es.attributes():
            print("no weighting given, assuming '1'")
            NETWORK.es["weight"] = 1
    else:
        print("Please provide graphml file")
        sys.exit(-1)


    def monitorFitness(ind, verbose=False):
        fit = np.sum(ind)
        if verbose:
            net = getNetwork()
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
        g = getNetwork()
        penalty = 0
        for edge in g.es():
            if not ind[edge.tuple[0]] and not ind[edge.tuple[1]]:
                if verbose:
                    print "penalty for edge {}: v{} -> v{} = {}".format(edge.index, edge.tuple[0], edge.tuple[1], edge["weight"])
                penalty += 2 * int(edge["weight"])
        return penalty


    def getNetwork():
        return NETWORK

    toolbox = base.Toolbox()
    #toolbox.register("map", futures.map)
    toolbox.register("attr_bool", np.random.randint, 2)
    toolbox.register("individual", tools.initRepeat,
                     creator.Individual, toolbox.attr_bool, n=NETWORK.vcount())
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    FITNESS = monitorFitness
    toolbox.register("evaluate", FITNESS)

    toolbox.register("mate", tools.cxOnePoint)
    toolbox.register("mutate", tools.mutFlipBit, indpb=0.2)
    toolbox.register("select", tools.selTournament, tournsize=10)



    pop, logbook = algorithms.eaSimple(toolbox.population(
    n=100), toolbox, cxpb=0.5, mutpb=0.5, ngen=5, verbose=False, stats=stats)
    return logbook
