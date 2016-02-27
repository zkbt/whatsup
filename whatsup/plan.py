from imports import *
from semester import Semester
from observatory import Observatory
from population import Interesting
from exopop.Confirmed import Confirmed
from planet import Planet
from matplotlib import animation


colors = ['salmon','darkgreen','cornflowerblue','gold',  'seagreen',  'mediumvioletred', 'crimson', 'firebrick', 'indigo', 'navy','orangered',   'purple' ]

class Plan(Talker):
    def __init__(self, semester='2015B', observatory='LCO', maxairmass=5, maxsun=10.0, directory='/Users/zkbt/Dropbox/proposals/observability/', name='default', start=None, finish=None):
        Talker.__init__(self)
        self.maxairmass = maxairmass
        self.maxsun = maxsun
        self.directory = directory
        zachopy.utils.mkdir(self.directory)
        # set up which semester we're talking about

        # set up our observatory
        self.observatory = Observatory(observatory, plan=self)

        self.semester = Semester(semester, plan=self, start=start, finish=finish)

        self.loadPopulation()
        self.selectInteresting()

    def clean(self, s):
        return s.replace(' ','').replace('-','')

    def loadPopulation(self):
        # set up the population
        self.known = Confirmed()
        '''self.known.standard.add_row(dict(name='WASP-94A b',
                        period=3.9501907, transit_epoch=2456416.39659,
                        teff=6153.0, stellar_radius=1.62, J=9.159,
                        planet_radius=1.72*zachopy.units.Rjupiter/zachopy.units.Rearth,
                        a_over_r=7.3488, planet_mass=0.452*zachopy.units.Mjupiter/zachopy.units.Mearth,
                        radius_ratio=0.109, b=0.17,
                        ra=313.78308, dec=-34.135528))'''



        for k in self.known.standard:
            k['name'] = self.clean(k['name'])
        self.known.propagate()

        # tidy up junk
        possible = (self.known.dec < self.observatory.latitude.value + 60.0)
        ok = (self.known.J > 0)*(self.known.a_over_r > 0)*possible*(self.known.dec*astropy.units.deg > self.observatory.latitude - 60.0*astropy.units.deg)
        self.known.standard = self.known.standard[ok]

        self.known.propagate()

    def selectInteresting(self, table=None, filter=None, list=None):

        if table is None:
            if list is None:
                if filter == None:
                    filter = self.known.name == 'WASP-94A b'
                table = self.known.standard[filter]
            else:
                cleaned = [self.clean(l) for l in list]
                toselect = astropy.table.Table(dict(name=cleaned))
                table = astropy.table.join(self.known.standard, toselect)

        # pull out the interesting targets
        self.interesting = Interesting(table)
        self.populatePlanets()


    def populatePlanets(self):
        self.planets = []
        for i in range(len(self.interesting.standard)):
            name = self.interesting.name[i]
            try:
                this_planet = Planet(self.interesting.standard[i],
                    color=colors[i % len(colors)], plan=self)
                assert(np.isfinite(this_planet.period))
                assert(np.isfinite(this_planet.duration))
                self.planets.append(this_planet)
            except (ValueError,AssertionError):
                print "UH-OH! Something went wrong on {0}".format(name)

    def findTransits(self):
        for planet in self.planets:
            planet.findTransits(self.semester.start, self.semester.finish)
            planet.filterTransits()


    def printTransits(self):
        for p in self.planets:
            p.speak(p.name)
            for t in p.transits:
                t.details()
                #(t.posttransit - t.pretransit).value*24))
                #self.observatory.sun(t.pretransit).alt.deg[0],
                #self.observatory.sun(t.posttransit).alt.deg[0]))


    def plotTransits(self):
        self.speak('plotting transits')
        self.findTransits()
        plt.ion()

        # set up the plotting windows
        self.figure = plt.figure('upcoming transits', figsize=(10, 4))
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
        self.ax['transits'].set_ylim(-1, len(self.planets))

        for k in self.ax.keys():
            self.observatory.plotSun(times=self.semester.times, ax=self.ax[k])

        fmt =  plt.matplotlib.dates.DateFormatter('%Y%m%d\n%H:%M')
        self.ax['airmass'].xaxis.set_major_formatter(fmt)
        f = plt.gcf()
        f.autofmt_xdate(rotation=90)
        #assert(False)
        plt.draw()

    def movie(self, fps=10, bitrate=10000, filename=None):
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
