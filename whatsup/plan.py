from .imports import *
from .semester import Semester
from .observatory import Observatory
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
                    pop=None,
                    start=None, finish=None,
                    observatory='SBO',
                    maxairmass=2.5,
                    maxsun=-12.0,
                    directory='observability/',
                    name='default'):

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
        self.semester = Semester(start=start, finish=finish, plan=self)

        # load the population of planets
        self.population = pop or Confirmed()

        # tidy up that population
        self.tidyPopulation()
        self.populatePlanets()

        # print out a summary of this plan
        self.describeInputs()

    def describeInputs(self):
        '''print text to terminal describing this observing plan'''

        self.speak('Observatory is {}'.format(self.observatory))
        self.speak('Time range spans {} to {}'.format(self.semester.start, self.semester.finish))
        self.speak('Population contains {} objects'.format(len(self.population.standard)))

    def tidyPopulation(self):
        '''load a population of exoplanets, defaulting to the list
        of confirmed transiting planets from the NASA Exoplanet Archive'''


        # clean the names of all the transiting planets
        for k in self.population.standard:
            k['name'] = clean(k['name'])

        # remove planets that are impossible to see from this latitude
        deg = astropy.units.deg
        zenith = np.abs(self.population.dec*deg - self.observatory.latitude)
        possible = zenith < 60.0*deg
        self.speak('{}/{} targets are visible from {} latitude'.format(
                            np.sum(possible), len(possible),
                            self.observatory.latitude))


        # trim the population
        self.population.standard = self.population.standard[possible]
        self.population.propagate()

        self.speak('the trimmed population contains {} objects'.format(
                        len(self.population.standard)))


    def populatePlanets(self):
        '''create a bunch of Planet objects, from the table'''
        self.planets = []
        for i in range(len(self.population.standard)):
            name = self.population.name[i]
            try:
                this_planet = Planet(self.population.standard[i],
                    color=colors[i % len(colors)], plan=self)
                assert(np.isfinite(this_planet.period))

                try:
                    assert(np.isfinite(this_planet.duration))
                    assert(np.isfinite(this_planet.transit_epoch))
                    assert(np.isfinite(this_planet.period))
                    self.planets.append(this_planet)

                except AssertionError:
                    self.speak(f'skipping {name} because its ephemeris is messy')
                    self.speak(f'(P={this_planet.period}, T0={this_planet.transit_epoch}, duration={this_planet.duration})')


            except (ValueError,AssertionError):
                print("UH-OH! Something went wrong on {0}".format(name))


    def findTransits(self, remake=False):
        '''identify all the transits for all the planets'''

        try:
            assert(self.transitsfound)
            assert(remake == False)
        except (AssertionError, AttributeError):
            self.speak('identifying transits among all the planets')
            for planet in self.planets:
                planet.findTransits(self.semester.start, self.semester.finish)
                planet.filterTransits()
            self.transitsfound = True


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


    def movieTransits(self, fps=10, bitrate=10000, filename=None):
        '''
        Make a movie of the whole semester,
        showing all the transits for your population.
        '''

        self.speak('plotting transits')
        self.findTransits()
        plt.ioff()

        # set up the plotting window (one night at a time)
        self.figure = plt.figure('upcoming transits', figsize=(15, 6), dpi=200)
        self.gs = plt.matplotlib.gridspec.GridSpec(2,1, hspace=0, wspace=0, height_ratios=[0.3, 1.0], bottom=0.35)
        self.ax = {}

        # an ax to include the names of the planets
        self.ax['transits'] = plt.subplot(self.gs[0])
        plt.setp(self.ax['transits'].get_xticklabels(), visible=False)
        plt.setp(self.ax['transits'].get_yticklabels(), visible=False)
        self.ax['transits'].plot_date([],[])
        plt.setp(self.ax['transits'].get_xaxis(), visible=False)
        plt.setp(self.ax['transits'].get_yaxis(), visible=False)
        self.ax['transits'].set_title('Observability from {0}'.format(self.observatory.name, self.semester.name))

        # an ax to include the airmass curves
        self.ax['airmass'] = plt.subplot(self.gs[1],
            sharex=self.ax['transits'])
        self.ax['airmass'].set_ylabel('Airmass')

        # plot all the individual transits for all the planets
        for i in range(len(self.planets)):
            self.planets[i].plotTransits(y=i)

        # nudge the limits on the transit labels
        # self.ax['transits'].set_xlim(self.semester.start.plot_date, self.semester.finish.plot_date)
        self.ax['transits'].set_ylim(-0.1*len(self.planets), 1.2*len(self.planets))

        # plot black bars to mask out when the Sun is up
        for k in self.ax.keys():
            self.observatory.plotSun(jd=self.semester.times, ax=self.ax[k])

        # set the formatting on the time label
        fmt =  plt.matplotlib.dates.DateFormatter('%Y-%m-%d\n%H:%M UT')
        self.ax['airmass'].xaxis.set_major_formatter(fmt)
        f = plt.gcf()
        f.autofmt_xdate(rotation=90)
        plt.tight_layout()


        self.speak('making a movie of transits')

        # initialize the animator
        metadata = dict(title='Observability from {0}'.format(self.observatory.name),
                        artist='whatsup')
        self.writer = animation.FFMpegWriter(fps=fps, metadata=metadata, bitrate=bitrate)
        if filename is None:
            filename = self.directory + 'transits-{}planets.mp4'.format(len(self.planets))
        self.speak('trying to save movie to {0}'.format(filename))
        with self.writer.saving(self.figure, filename, self.figure.get_dpi()):
            # loop over exposures
            window = 7/24.0

            # approximate kludge; no daylight savings; need to incorporate time zones
            offset = self.observatory.standardzone.to('day').value

            for m in tqdm(self.semester.midnights):
                xlim = self.ax['airmass'].get_xlim()
                center = Time(m, format='jd').plot_date + offset
                self.ax['airmass'].set_xlim((center - window), (center + window))

                nightof = Time(m - 0.5, format='jd').iso.split()[0]
                self.ax['transits'].set_title('Observability from {} on {}'.format(self.observatory.name, nightof))
                self.writer.grab_frame()
