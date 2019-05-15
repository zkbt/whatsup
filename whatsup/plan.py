from .imports import *
from .semester import Semester
from .observatory import Observatory
from .population import Interesting
from exopop.Confirmed import Confirmed
from .planet import Planet
from matplotlib import animation

# a list of colors to give transits (will repeat)
colors = [  'salmon',
            'firebrick',
            'hotpink',
            'mediumvioletred',
            'coral',
            'orangered',
            'darkorange',
            'plum',
            'fuchsia',
            'darkviolet',
            'purple',
            'indigo',
            'slateblue',
            'limegreen',
            'seagreen',
            'darkgreen',
            'olive',
            'teal',
            'steelblue',
            'royalblue',
            'sandybrown',
            'chocolate',
            'saddlebrown',
            'maroon']

class Plan(Talker):
    '''a Plan object to keep track of potentially observable transits'''

    def __init__(self,
                    semester='2015B',
                    observatory='LCO',
                    maxairmass=5,
                    maxsun=10.0,
                    directory='/Users/zkbt/Dropbox/proposals/observability/',
                    name='default',
                    start=None,
                    finish=None):

        '''initialize, setting the observatory, semester, and population'''

        # initialize the talking setup
        Talker.__init__(self)

        # set the maximum airmass and the maximum sun altitude
        self.maxairmass = maxairmass
        self.maxsun = maxsun

        # set up a directory to store results in
        self.directory = directory
        craftroom.utils.mkdir(self.directory)

        # set up our observatory
        self.observatory = Observatory(observatory, plan=self)

        # set up the time range this should cover
        self.semester = Semester(semester, plan=self, start=start, finish=finish)

        # load the population of planets
        self.loadPopulation()
        self.selectInteresting()

        # print out a summary of this plan
        self.describeInputs()

    def describeInputs(self):
        '''print text to terminal describing this observing plan'''

        self.speak('Observatory is {}'.format(self.observatory))
        self.speak('Time range spans {} to {}'.format(self.semester.start, self.semester.finish))
        self.speak('Population contains {} objects'.format(len(self.known.standard)))

    def loadPopulation(self, pop=Confirmed):
        '''load a population of exoplanets, defaulting to the list
        of confirmed transiting planets from the NASA Exoplanet Archive'''

        # set up the population
        self.known = pop()

        # clean the names of all the transiting planets
        for k in self.known.standard:
            k['name'] = clean(k['name'])

        # propagate the changed names through the population
        self.known.propagate()

        # remove planets that are impossible to see from this latitude
        deg = astropy.units.deg
        zenith = np.abs(self.known.dec*deg - self.observatory.latitude)
        possible = zenith < 60.0*deg
        self.speak('{}/{} targets are visible from {} latitude'.format(
                            np.sum(possible), len(possible),
                            self.observatory.latitude))

        # get rid of junky entries
        notjunky = (self.known.J > 0)*(self.known.a_over_r > 0)
        ok = notjunky*possible
        self.speak('{} otherwise visible targets were junk'.format(
                        np.sum(possible)-np.sum(ok)))

        # trim the population
        self.known.standard = self.known.standard[ok]
        self.known.propagate()
        self.speak('the trimmed population contains {} objects'.format(
                        len(self.known.standard)))


    def selectInteresting(self, table=None, filter=None, list=None):
        '''specify which of the planets are interesting
                table = a exopop style standard table
                filter = indices or a mask, for the known table
                list = a list of names to select
        '''


        if table is None:
            if list is None:
                if filter == None:
                    filter = self.known.name == 'WASP-94A b'
                table = self.known.standard[filter]
            else:
                cleaned = [clean(l) for l in list]
                toselect = astropy.table.Table(dict(name=cleaned))
                table = astropy.table.join(self.known.standard, toselect)

        # pull out the interesting targets
        self.interesting = Interesting(table)
        self.populatePlanets()

    def populatePlanets(self):
        '''create a bunch of Planet objects, from the table'''
        self.planets = []
        for i in range(len(self.interesting.standard)):
            name = self.interesting.name[i]
            try:
                this_planet = Planet(self.interesting.standard[i],
                    color=colors[i % len(colors)], plan=self)
                assert(np.isfinite(this_planet.period))
                self.planets.append(this_planet)

                try:
                    assert(np.isfinite(this_planet.duration))
                except AssertionError:
                    print(name, this_planet.duration, this_planet.a_over_r)

            except (ValueError,AssertionError):
                print("UH-OH! Something went wrong on {0}".format(name))


    def findTransits(self):
        '''identify all the transits for all the planets'''
        self.speak('identifying transits among all the planets')
        for planet in self.planets:
            planet.findTransits(self.semester.start, self.semester.finish)
            planet.filterTransits()


    def printTransits(self, filename='upcoming_transits.txt'):
        '''print all the observable transits'''
        with open(filename, 'w') as f:
            for p in self.planets:
                p.speak(p.name)
                for t in p.transits:
                    s = t.details()
                    f.write(s + '\n')
                #(t.posttransit - t.pretransit).value*24))
                #self.observatory.sun(t.pretransit).alt.deg[0],
                #self.observatory.sun(t.posttransit).alt.deg[0]))


    def plotTransits(self):
        '''plot the transits, on one massive plot'''
        self.speak('plotting transits')
        self.findTransits()
        plt.ion()

        # set up the plotting windows
        self.figure = plt.figure('upcoming transits', figsize=(10, 4), dpi=300)
        self.gs = plt.matplotlib.gridspec.GridSpec(2,1, hspace=0, wspace=0, height_ratios=[0.3, 1.0], bottom=0.35)
        self.ax = {}

        self.ax['transits'] = plt.subplot(self.gs[0])
        plt.setp(self.ax['transits'].get_xticklabels(), visible=False)
        plt.setp(self.ax['transits'].get_yticklabels(), visible=False)
        self.ax['transits'].plot_date([],[])
        plt.setp(self.ax['transits'].get_xaxis(), visible=False)
        plt.setp(self.ax['transits'].get_yaxis(), visible=False)
        self.ax['transits'].set_title('Observability from {0}'.format(self.observatory.name, self.semester.name))

        self.ax['airmass'] = plt.subplot(self.gs[1],
            sharex=self.ax['transits'])
        self.ax['airmass'].set_ylabel('Airmass')

        for i in range(len(self.planets)):
            self.planets[i].plotTransits(y=i)

        self.ax['transits'].set_xlim(self.semester.start.plot_date, self.semester.finish.plot_date)
        self.ax['transits'].set_ylim(-0.1*len(self.planets), 1.2*len(self.planets))

        for k in self.ax.keys():
            self.observatory.plotSun(times=self.semester.times, ax=self.ax[k])

        fmt =  plt.matplotlib.dates.DateFormatter('%Y%m%d\n%H:%M')
        self.ax['airmass'].xaxis.set_major_formatter(fmt)
        f = plt.gcf()
        f.autofmt_xdate(rotation=90)
        #assert(False)
        plt.draw()

    def movie(self, fps=10, bitrate=10000, filename=None):
        '''make a movie of the massive plot of transits'''

        plt.ioff()
        self.speak('making a movie of transits')
        # initialize the animator
        metadata = dict(title='Observability from {0}'.format(self.observatory.name), artist='Z.K.B.-T.')
        self.writer = animation.FFMpegWriter(fps=fps, metadata=metadata, bitrate=bitrate)
        if filename is None:
            filename = self.directory + '{0}_{1}planets.mp4'.format(self.semester.name, len(self.planets))
        self.speak('trying to save movie to {0}'.format(filename))
        with self.writer.saving(self.figure, filename, self.figure.get_dpi()):
            # loop over exposures
            window = 8*astropy.units.hour

            for m in self.semester.midnights:
                self.speak('adding movie frame for {0}'.format(m.jyear))
                xlim = self.ax['airmass'].get_xlim()
                self.ax['airmass'].set_xlim((m - window).plot_date, (m + window).plot_date)
                plt.draw()
                self.writer.grab_frame()
