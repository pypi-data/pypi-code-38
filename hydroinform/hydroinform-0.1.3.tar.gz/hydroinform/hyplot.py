# -*- coding: utf-8 -*-
from hydroinform.hymod import *
import matplotlib.pyplot as plt


class PlanPlot():
    def __init__(self, reaches = [], fig=None, position=111, show=False, xssPlot=None, profilePlot=None, dem=None, showWaterLevel=False, show_normal_depths=False):
        self.dem = dem #digital elevation model as background (xx, yy, dem)
        self.reaches = reaches
        self.fig = fig
        self.show = show
        self.position = position
        self.xssPlot = xssPlot
        self.profilePlot = profilePlot
        if self.fig is None:
            self.fig = plt.figure()
        self.ax = self.fig.add_subplot(self.position)
        self.ax.set_aspect('equal', 'datalim')
        self.pathcolls = []
        self.firstTimeOnReachPickEvent = True
        self.yellowLine = None # The yellow marker that indicates which crosssection that is selected.
        self.pickedReachIndex = None
        self.pickedXsIndex = None
        self.fig.canvas.mpl_connect('pick_event', self.on_reachpick)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.showWaterLevel = showWaterLevel
        self.show_perimenter_points = False
        self.show_normal_depths = show_normal_depths
        self.plot()

    def on_reachpick(self, event):
        if self.xssPlot is None:
            self.xssPlot = XssPlot()
            self.xssPlot.showWaterLevel = self.showWaterLevel
            print('created new xss plot')

        if self.profilePlot is None:
            self.profilePlot = ProfilePlot()
            self.profilePlot.showWaterLevel = self.showWaterLevel
            self.profilePlot.show_normal_depths = self.show_normal_depths
            print('created new profile plot')

        self.pickedReachIndex = self.pathcolls.index(event.artist)
        self.pickedXsIndex = event.ind[0]
        self.ax.set_title(self.reaches[self.pickedReachIndex].name)
        pickedXs = self.reaches[self.pickedReachIndex].xss[self.pickedXsIndex]
        self.profilePlot.update(self.reaches[self.pickedReachIndex], pickedXs)
        self.xssPlot.update(pickedXs)
        if self.firstTimeOnReachPickEvent:
            self.firstTimeOnReachPickEvent = False
            self.yellowLine, = self.ax.plot([pickedXs.x], [pickedXs.y], marker='o', color='y')
            plt.show()
        else:
            self.yellowLine.set_data([pickedXs.x], [pickedXs.y])
            self.fig.canvas.draw()

    def on_key_press(self, event):
        print('press', event.key)
        if (event.key == 'right' or event.key == 'left') and self.firstTimeOnReachPickEvent == False:
            if event.key == 'right':
                if self.pickedXsIndex == len(self.reaches[self.pickedReachIndex].xss) - 1:
                    self.pickedXsIndex = 0
                else:
                    self.pickedXsIndex += 1
            elif event.key == 'left':
                if self.pickedXsIndex == 0:
                    self.pickedXsIndex = len(self.reaches[self.pickedReachIndex].xss) - 1
                else:
                    self.pickedXsIndex -= 1

            pickedXs = self.reaches[self.pickedReachIndex].xss[self.pickedXsIndex]
            self.xssPlot.update(pickedXs)
            self.profilePlot.update(self.reaches[self.pickedReachIndex], pickedXs)
            self.yellowLine.set_data([pickedXs.x], [pickedXs.y])
            self.fig.canvas.draw()


    def plot(self):
        for reach in self.reaches:
            if self.dem:
                contour_levels = np.arange(-2, 2, 0.1)
                self.ax.contourf(self.dem[0], self.dem[1], self.dem[2], contour_levels, cmap='terrain', zorder=0)
            self.ax.plot([p.x for p in reach.riverPoints], [p.y for p in reach.riverPoints], color='b', zorder=1)
            pathcoll = self.ax.scatter([p.x for p in reach.xss], [p.y for p in reach.xss], marker='o', color='b', picker=5)
            self.ax.scatter([xs.x for xs in reach.xss if xs.is_closed], [xs.y for xs in reach.xss if xs.is_closed], marker='o', color='green', zorder=2) #Marking xs which are closed
            self.ax.scatter([xs.x for xs in reach.xss if xs.is_weir], [xs.y for xs in reach.xss if xs.is_weir], marker='o', color='red', zorder=3)  # Marking xs which are weirs
            self.pathcolls.append(pathcoll)
            if self.show_perimenter_points is True:
                for reach in self.reaches:
                    for xs in reach.xss:
                        self.ax.plot([pp.x for pp in xs.pps], [pp.y for pp in xs.pps], marker='x', color='green', zorder=0)

        if self.show:
            plt.show()


class XssPlot():
    def __init__(self, xss = [], fig=None, position=111, show=False, showWaterLevel=False):
        self.xss = xss
        self.position = position
        self.show = show
        self.showWaterLevel = showWaterLevel
        self.ax = None
        self.fig = fig
        if self.fig == None:
            self.fig = plt.figure()
        self.ax = self.fig.add_subplot(self.position)
        self.fig.canvas.mpl_connect('key_press_event', self.press)
        self.plot()
        print('XssPlot __init__(...) completed.')

    def press(self, event):
        if event.key == 'escape':
            lastXs = self.xss[-1]
            self.xss = [lastXs]
            self.ax.clear()
            self.plot()

    def plot(self):
        if len(self.xss) > 0:
            for n in range(len(self.xss) - 1):
                xp, zp = [p.dx for p in self.xss[n].pps], [p.dz + self.xss[n].z for p in self.xss[n].pps]
                self.ax.plot(xp, zp, color='gray', zorder=0)
                self.ax.scatter(xp, zp, color='gray', zorder=0)

            self.ax.plot([p.dx for p in self.xss[-1].pps], [p.dz + self.xss[-1].z for p in self.xss[-1].pps], color='k', zorder=1)
            self.ax.scatter([p.dx for p in self.xss[-1].pps], [p.dz + self.xss[-1].z for p in self.xss[-1].pps], color='k', zorder=1)

            leftbank_points = [p for p in self.xss[-1].pps if p.marker == 'left bank']
            self.ax.scatter([p.dx for p in leftbank_points], [p.dz + self.xss[-1].z for p in leftbank_points], color='r', marker='o', zorder=2)
            rightbank_points = [p for p in self.xss[-1].pps if p.marker == 'right bank']
            self.ax.scatter([p.dx for p in rightbank_points], [p.dz + self.xss[-1].z for p in rightbank_points], color='b', marker='o',zorder=2)
            center_points = [p for p in self.xss[-1].pps if p.marker == 'center']
            self.ax.scatter([p.dx for p in center_points], [p.dz + self.xss[-1].z for p in center_points], color='y', marker='o',zorder=2)

            if self.showWaterLevel:
                wps = self.xss[-1].get_wetted_polygon(self.xss[-1].depth)
                self.ax.fill([p.dx for p in wps], [p.dz + self.xss[-1].z for p in wps], zorder=0)

            if self.xss[-1].is_closed:
                is_closed_str = 'closed xs'
            else:
                is_closed_str = 'open xs'
            self.ax.set_title('Chainage: ' + str(self.xss[-1].chainage) + ' ' + is_closed_str)
            self.fig.canvas.draw()

            if self.show:
                plt.show()

    def update(self, xs):
        self.ax.clear()
        while xs in self.xss:
            self.xss.remove(xs)

        self.xss.append(xs)

        print('updated XssPlot')
        self.plot()


class ProfilePlot():
    def __init__(self, reach=None, fig=None, position=111, showBanks=True, showWaterLevel = False, show=True, show_normal_depths=False):
        self.reach = reach
        self.position = position
        self.show = show
        self.showBanks = showBanks
        self.showWaterLevel = showWaterLevel
        self.show_normal_depths = show_normal_depths
        self.ax = None
        self.fig = fig
        self.yellowLine = None  # The yellow marker that indicates which crosssection that is selected.
        if self.fig is None:
            self.fig = plt.figure()
        self.ax = self.fig.add_subplot(self.position)
        self.plot()

    def plot(self):
        if self.reach != None:
            chainages = [xs.chainage for xs in self.reach.xss]
            zmins = [xs.z for xs in self.reach.xss]
            self.ax.plot(chainages, zmins, color='k', marker='o', zorder=1)
            self.ax.scatter([xs.chainage for xs in self.reach.xss if xs.is_closed], [xs.z for xs in self.reach.xss if xs.is_closed], marker='o', color='green', zorder=2)  # Marking xs which are closed
            self.ax.scatter([xs.chainage for xs in self.reach.xss if xs.is_weir], [xs.z for xs in self.reach.xss if xs.is_weir], marker='o', color='red', zorder=3)  # Marking xs which are weirs

            if self.showBanks:
                self.ax.plot(chainages, [xs.pps[0].dz + xs.z for xs in self.reach.xss], '--', color='k')
                self.ax.plot(chainages, [xs.pps[-1].dz + xs.z for xs in self.reach.xss], '--', color='k')

            if self.showWaterLevel:
                if len(self.reach.calculated_water_levels) == 0:
                    self.ax.plot(chainages, [xs.depth + xs.z for xs in self.reach.xss], color='b', zorder=10, label='calculated water level')
                else:
                    self.ax.plot([wl[0] for wl in self.reach.calculated_water_levels],[wl[1] for wl in self.reach.calculated_water_levels], color='b', zorder=10)

            # for observation in self.reach.observations:
            #     self.ax.scatter([a[0] for a in observation.chainage_waterlevels], [a[1] for a in observation.chainage_waterlevels], marker='o', color='red', label=observation.name, zorder=20)

            self.ax.scatter([a[0] for a in self.reach.observations], [a[1] for a in self.reach.observations], marker='o', color='red', label='Observed', zorder=20)

            if self.show_normal_depths:
                chs = []
                normal_depths = []
                for n in range(len(self.reach.xss) - 1):
                    slope = (self.reach.xss[n + 1].z - self.reach.xss[n].z) / (self.reach.xss[n + 1].chainage - self.reach.xss[n].chainage)
                    if slope > 0.:
                        chs.append((self.reach.xss[n].chainage + self.reach.xss[n + 1].chainage) / 2.)
                        z_mean = (self.reach.xss[n].z + self.reach.xss[n + 1].z) / 2.
                        normal_depths.append(z_mean + self.reach.xss[n].get_normal_depth(slope))
                self.ax.scatter(chs, normal_depths, marker='o', color='green', label='Normal depth')

            # if showLabels:
            #     for i, j in zip(chainages, zmins):
            #         ax.annotate('%s)' % j, xy=(i, j), xytext=(30, 0), textcoords='offset points')
            #         ax.annotate('(%s,' % i, xy=(i, j))
            #
            # if showGrid:
            #     ax.grid()
            self.ax.legend()

            self.ax.set_title(self.reach.name)
            self.fig.canvas.draw()
            if self.show is True:
                plt.show()

    def update(self, reach, xs):
        # if reach != self.reach: TODO: linjerne er udkommenteret da det ellers ikke virker, men figuren flikker...
            self.ax.clear()
            self.reach = reach
            self.yellowLine, = self.ax.plot([xs.chainage],[xs.z], marker='o', color='y', linestyle=' ', zorder=3)
            self.plot()

        # else:
        #     self.yellowLine.set_data([xs.chainage], [xs.z])
        #     self.fig.canvas.draw()



def plot(obj, show=True, showWaterLevel=False, use_seperate_windows=False, show_normal_depths=False, dem=None):  # Plotting whatever is passed as obj
    """
    General plotting of hymod related data. Depending on the object type passed different plot types is shown. However,
    normally you will pass an object of type hymod.Reach_network. This will generate a plot with three subplots. A plan
    plot, a cross section plot and a profile plot. When clicking on a cross section in the plan plot, the cross section
    plot and the profile plot will show the associated cross section and reach, respectively. The cross section plot
    includes history, which means that previously selected cross sections is shown in a grey color. Pressing the escape
    key will clear the history. You can use right arrow and left arrow keys to navigate to the next cross section in a
    reach. In the plan plot and the profile black dots are open cross sections, green dots are closed cross sections and
    red dots are weirs. River banks are shown as dashed black lines. Observed water levels is shown in the profile plot
    if the property hymod.Reach.Observations is populated (see further documentation for this in the Reach code)
    :param obj: object instances of types allowed: hymod.Xs, [hymod.Xs], hymod.Reach, [hymod.Reach], hymod.Reach_network
    :param show: For most cases leave this as the default True value. If false the plot is not shown. (used in special cases)
    :param showWaterLevel: When True, calculated water levels are shown in profile plots and cross sections plots
    :param use_seperate_windows: When False: All plots are shown in the same figure. When True three seperate windows appear
    :param show_normal_depths: When True, normal depth are shown as scatter points in the profile plot
    """
    if isinstance(obj, Xs):  # a single crosssection
        XssPlot([obj], show=show, showWaterLevel=showWaterLevel).plot()

    elif isinstance(obj, list) and isinstance(obj[0], Xs):  # a list of crosssections
        XssPlot(obj, show=show, showWaterLevel=showWaterLevel).plot()

    elif isinstance(obj, Reach): # a single reach
        PlanPlot([obj], show=show, showWaterLevel=showWaterLevel, show_normal_depths=show_normal_depths).plot()

    elif isinstance(obj, list) and isinstance(obj[0], Reach): # a list of reaches
        PlanPlot(obj, show=show, showWaterLevel=showWaterLevel, show_normal_depths=show_normal_depths).plot()

    elif isinstance(obj, Reach_network):
        if use_seperate_windows:
            xsPlot = XssPlot(fig=plt.figure(), position=111, showWaterLevel=showWaterLevel)
            profilePlot = ProfilePlot(fig=plt.figure(), position=111, showWaterLevel=showWaterLevel, show_normal_depths=show_normal_depths)
            planPlot = PlanPlot(reaches=obj.reaches, fig=plt.figure(), position=111, xssPlot=xsPlot, profilePlot=profilePlot, dem=dem)

        else:
            fig = plt.figure()
            xsPlot = XssPlot(fig=fig, position=222, showWaterLevel=showWaterLevel)
            profilePlot = ProfilePlot(fig=fig, position=212, showWaterLevel=showWaterLevel, show_normal_depths=show_normal_depths)
            planPlot = PlanPlot(reaches=obj.reaches, fig=fig, position=221, xssPlot=xsPlot, profilePlot=profilePlot, dem=dem)

        if show:
            plt.show()
    else:
        raise TypeError('non recognized type passed to plot function')

#TODO: dette er et midlertidig hack. Jeg tror at de skal laves med et object og ikke med en static method, saa man kan saette flere parametre (e.g. contour levels etc.)
# def plot_reach_network(reach_network, show=True, showWaterLevel=False, dem=None):
#     fig = plt.figure()
#     xsPlot = XssPlot(fig=fig, position=222, showWaterLevel=showWaterLevel)
#     profilePlot = ProfilePlot(fig=fig, position=212, showWaterLevel=showWaterLevel)
#     planPlot = PlanPlot(reaches=reach_network.reaches, fig=fig, position=221, xssPlot=xsPlot, profilePlot=profilePlot, dem=dem)
#     if show:
#         plt.show()

