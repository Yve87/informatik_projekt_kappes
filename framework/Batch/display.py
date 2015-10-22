from pylab import *
from mpl_toolkits.mplot3d import axes3d, Axes3D
from mpl_toolkits.mplot3d.axes3d import get_test_data
import numpy
from itertools import cycle
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import results


class Plotter():

    """
    Displays specific GA plots with matplotlib.

    Imortant note: proper **otherFixedParams must be passed in or the plot will have spooky results

    Line styles:
    '', ' ', 'None', '--', '-.', '-', ':'

    Possible Options:
    xAxis - name of the column to use for the xAxis
    yAxis - name of the column to use for the xAxis
    zAxis - name of the column to use for the yAxis

    xLabel
    yLabel
    zLabel

    xLimit
    yLimit
    zLimit

    """
    lineColors = ['b', 'g', 'r', 'm', 'y', 'c']
    lineColors_cycle = cycle(lineColors)

    lineStyles = ["-", "--", "-.", ":"]
    lineStyles_cycle = cycle(lineStyles)

    markerStyles = ['o', 'v', '^', '3', '8', 's', '*', '+']
    markerStyles_cycle = cycle(markerStyles)

    def __init__(self, isIon=False):
        """
        Constructor for Plotter.

        :param isIon: Set to true if running a realtime plot environment
        """
        if(isIon):
            plt.ion()
        self.fig = plt.figure(1)
        self.fig.set_facecolor((1, 1, 1))

        self.is3D = None

    def setAxisLabels(self, xLabel="", yLabel="", zLabel=""):
        """
        Sets the axis labels for the current working plot.
        :param xLabel: x axis label
        :param yLabel: y axis label
        :param zLabel: z axis label
        """
        self.ax.set_xlabel(xLabel)
        self.ax.set_ylabel(yLabel)

        if("set_zlabel" in dir(self.ax)):
            self.ax.set_zlabel(zLabel)

    def setAxisLimits(self, **options):
        """
        Sets the axis limits for the current working plot. Usefull for a realtime updated plot.
        :param xLim: x axis limit. Example xLim=[0,1]
        :param yLim: y axis limit. Example yLim=[2,1000]
        :param zLim: z axis limit. Example zLim=[0,100]
        """
        if(options.get("xLim") != None):
            self.ax.set_xlim(options.get("xLim"))
        if(options.get("yLim") != None):
            self.ax.set_ylim(options.get("yLim"))
        if(options.get("zLim") != None):
            self.ax.set_zlim(options.get("zLim"))

    def addLegend(self, legendArray):
        """
        Adds a legend to the current plot matching the given legendArray.

        :param legendArray: array of line names
        """
        plt.legend(legendArray, loc="center left", bbox_to_anchor=(1, 0.6))
        box = self.ax.get_position()
        self.ax.set_position([box.x0, box.y0, box.width * 0.75, box.height])

    def setGrid(self, onOff):
        """
        Turns the grid on or off.
        """
        self.ax.grid(onOff)

    def plot_2D(self, filter, **options):
        """
            2D plot against two axis.


            :param: colLine:
            :param lineStyle:
            Returns the drawing axis
        """

        if(len(filter) != 2):
            raise Exception("Graph creation filters created wrong number of columns")

        if self.is3D == None:
            self.__use2D()

        colNames = filter.keys()
        xAxis = options.get("xAxis", colNames[0])
        yAxis = options.get("yAxis", colNames[1])

        x = filter[xAxis]
        y = filter[yAxis]

        self.ax.plot(x, y, options.get("colLine", Plotter.lineColors_cycle.next()) + options.get("lineStyle", '-'))

    def add_numberOfRunsLabel(self, numbRuns):
        """
        Adds a number_of_runs label to the plot.
        :param numbRuns: 
        """
        # self.fig.text(0.1, -0.08, , horizontalalignment='center', verticalalignment='center', transform=self.ax.transAxes, fontsize=10)
        figtext(.02, .02, '(Each result averaged over ' + str(numbRuns) + ' runs.)')

    def add_nevalsLabel(self, filter):
        """
        Parses the filter for the "result_nevals" column and sums all the values to get the total nevals.
        Filter must contain "result_nevals" column.
        """
        result_nevals = results.Filter(filter, "result_nevals")["result_nevals"]

        figtext(.6, .02, 'nevals=' + str(sum(result_nevals)))

    def plot_3D(self, filter, **options):
        """
            Plots a 3D graph with the given filter. Filter must contain exactly 3 columns.

            :param filter: column object
            :param xAxis: the name of the column to use for the x axis
            :param yAxis: the name of the column to use for the y axis
            :param zAxis: the name of the column to use for the z axis
        """
        if self.is3D == None:
            self.__use3D()

        colNames = filter.keys()
        xAxis = options.get("xAxis", colNames[0])
        yAxis = options.get("yAxis", colNames[1])
        zAxis = options.get("zAxis", colNames[2])

        X = np.array(filter[xAxis])
        Y = np.array(filter[yAxis])
        Z = np.array(filter[zAxis])

        # X2, Y2, Z2 = Plotter.__createXYZ(X, Y, Z)

        # self.ax.plot_surface(X2, Y2, Z2, cmap=cm.coolwarm)
        # X = filter[xAxis]
        # Y = filter[yAxis]
        # Z = filter[zAxis]

        self.ax.plot_trisurf(X, Y, Z, range(5), cmap=cm.YlOrRd, linewidth=1)

    def plot_3D_Wireframe(self, filter, **options):
        """
            Plots a 3D wireframe graph with the given filter. Filter must contain exactly 3 columns.

            :param filter: column object
            :param xAxis: the name of the column to use for the x axis
            :param yAxis: the name of the column to use for the y axis
            :param zAxis: the name of the column to use for the z axis
        """
        if self.is3D == None:
            self.__use3D()

        colNames = filter.keys()
        xAxis = options.get("xAxis", colNames[0])
        yAxis = options.get("yAxis", colNames[1])
        zAxis = options.get("zAxis", colNames[2])

        X = np.array(filter[xAxis])
        Y = np.array(filter[yAxis])
        Z = np.array(filter[zAxis])

        X2, Y2, Z2 = Plotter.__createXYZ(X, Y, Z)

        self.ax.plot_surface(X2, Y2, Z2, rstride=1, cstride=1, antialiased=True, linewidth=1.0, alpha=0.1)

    def add_Heatmap(self, filter, **options):
        """
            Adds a heatmap to the XY axis plane of the current 3D plot.

            :param filter: column object
            :param xAxis: the name of the column to use for the x axis
            :param yAxis: the name of the column to use for the y axis
            :param zAxis: the name of the column to use for the z axis

            Note: doesn't work as expected with realtime update.
        """
        colNames = filter.keys()
        xAxis = options.get("xAxis", colNames[0])
        yAxis = options.get("yAxis", colNames[1])
        zAxis = options.get("zAxis", colNames[2])

        X = np.array(filter[xAxis])
        Y = np.array(filter[yAxis])
        Z = np.array(filter[zAxis])

        X2, Y2, Z2 = self.__createXYZ(X, Y, Z)

        zmin = np.min(np.min(Z2))
        zmax = np.max(np.max(Z2))
        zminplus = zmin - ((zmax - zmin) * 1.1)
        zmaxplus = zmax + ((zmax - zmin) * 1.1)
        self.ax.set_zlim(zminplus, zmaxplus)

        self.ax.plot_surface(X2, Y2, Z2, rstride=1, cstride=1, antialiased=True, linewidth=1.0, alpha=0.1)
        self.c = self.ax.contourf(X2, Y2, Z2, zdir='z', cmap=cm.YlOrRd, offset=zminplus)

    def add_Colorbar(self):
        """
        Adds colorbar legend for a heatmap
        Only works after add_Heatmap is called
        """
        self.fig.colorbar(self.c, shrink=0.5, aspect=5)

    @staticmethod
    def __createXYZ(X, Y, Z):
        """
        Private
        :param XYZ: tuple (X, Y, Z)
        """
        a = np.vstack((X, Y, Z)).T
        a = a[numpy.lexsort((a[:, 0], a[:, 1]))]
        X, Y, Z = a.T

        cols = np.unique(X).shape[0]
        while(len(X) % cols != 0):
            np.append(X, X[-1])
            np.append(Y, Y[-1])
            np.append(Z, Z[-1])

        X2 = X.reshape(-1, cols)
        Y2 = Y.reshape(-1, cols)
        Z2 = Z.reshape(-1, cols)
        return (X2, Y2, Z2)

    def clearAx(self):
        if("ax" in dir(self)):
            self.ax.cla()

    def __use3D(self):
        """
        Private
        """
        self.ax = self.fig.gca(projection='3d')
        self.is3D = True

    def __use2D(self):
        """
        Private
        """
        self.ax = self.fig.add_subplot(111)
        self.is3D = False

    def draw(self):
        """
        Use with ion() mode. Draws the plot to the graph view.
        """
        plt.draw()

    def show(self):
        """
        Shows the plot (blocking).
        """
        plt.draw()
        plt.show(block=True)

    def ion(self, onOff):
        """
        Turns interactive mode on or off.
        """
        if(onOff):
            plt.ion()
        else:
            plt.ioff()

    @staticmethod
    def savePDF(filePath, figure):
        """
            Saves the given figure as a PDF file
        """
        with PdfPages(filePath) as pdf:
            pdf.savefig(figure)

    @staticmethod
    def saveFigure(filePath, figure):
        """
            Saves the given figure. Extension of the filePath will define the file type.
        """
        figure.savefig(filePath)

    class Templates():

        """
        Static class containing templates for different GA plots.
        """

        @staticmethod
        def plot_3D_Mutpb_Cxpb(filter, useGeneration, show=False):
            filter = results.Filter(filter, "mutpb", "cxpb", "result_avg", result_gen=useGeneration)

            plotter = Plotter()
            plotter.plot_3D_Wireframe(filter, xAxis="mutpb", yAxis="cxpb", zAxis="result_avg")
            plotter.add_Heatmap(filter, xAxis="mutpb", yAxis="cxpb", zAxis="result_avg")
            plotter.add_Colorbar()
            plotter.add_numberOfRunsLabel(1)
            plotter.setAxisLabels(xLabel="Mutation Rate", yLabel="Crossover Rate", zLabel="Average Fitness")
            plotter.ax.view_init(elev=20, azim=-131)

            if(show):
                plotter.show()
            return plotter

        @staticmethod
        def plot_2D_Fit_vs_Gen__MultiMutpb(filter, everyNth=1, show=False):

            plotter = Plotter()

            allMutpbs = sorted(list(set(results.Filter(filter, "mutpb")['mutpb'])))[0::everyNth]
            legendArray = []
            print allMutpbs
            for mutpb in allMutpbs:
                plotter.plot_2D(results.Filter(filter, "result_gen", "result_avg", mutpb=mutpb), xAxis="result_gen", yAxis="result_avg", lineStyle=Plotter.lineStyles_cycle.next())
                legendArray.append("Mutpb = " + str(mutpb))

            plotter.addLegend(legendArray)
            plotter.setAxisLabels(xLabel="Generation", yLabel="Fitness Average")

            if(show):
                plotter.show()
            return plotter

        @staticmethod
        def plot_2D_Fit_vs_Gen__MultiCxpb(filter, everyNth=1, show=False):

            plotter = Plotter()

            allcxpbs = sorted(list(set(results.Filter(filter, "cxpb")['cxpb'])))[0::everyNth]
            legendArray = []
            print allcxpbs
            for cxpb in allcxpbs:
                plotter.plot_2D(results.Filter(filter, "result_gen", "result_avg", cxpb=cxpb), xAxis="result_gen", yAxis="result_avg", lineStyle=Plotter.lineStyles_cycle.next())
                legendArray.append("Cxpb = " + str(cxpb))

            plotter.addLegend(legendArray)
            plotter.setAxisLabels(xLabel="Generation", yLabel="Fitness Average")

            if(show):
                plotter.show()
            return plotter

        @staticmethod
        def plot_2D_Fit_vs_Gen_MinMaxAvg(filter, show=False):

            plotter = Plotter()

            legendArray = ["Minimum Fitness", "Average Fitness", "Maxmimum Fitness"]
            plotter.plot_2D(results.Filter(filter, "result_gen", "result_min"), xAxis="result_gen", yAxis="result_min", lineStyle="-")
            plotter.plot_2D(results.Filter(filter, "result_gen", "result_avg"), xAxis="result_gen", yAxis="result_avg", lineStyle="-")
            plotter.plot_2D(results.Filter(filter, "result_gen", "result_max"), xAxis="result_gen", yAxis="result_max", lineStyle="-")
            plotter.addLegend(legendArray)
            plotter.setAxisLabels(xLabel="Generation", yLabel="Fitness")

            if(show):
                plotter.show()
            return plotter
