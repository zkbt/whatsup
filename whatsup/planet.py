from .imports import *
from exopop.Population import Population
from .transit import Transit

class Interesting(Population):
    """
    The Interesting object, for keeping track planets worth observing.
    """
    def __init__(self, filtered):
        Talker.__init__(self)
        # don't do the default Population initialization
        self.standard = filtered
        self.propagate()

class Planet(Interesting):
    def __init__(self, row, color='red', plan=None):
        Interesting.__init__(self, row)

        # store the ephemeris
        self.period = row['period'] # days
        self.transit_epoch = row['transit_epoch'] # bjd

        # store how this should be displayed
        self.color = color

        # store where the start is on the sky
        self.coord = astropy.coordinates.SkyCoord(self.ra*astropy.units.deg, self.dec*astropy.units.deg)

        # connect to the plan
        self.plan = plan


    def epoch(self, time):
        '''
        Figure out the epoch of the closest transit to a particular time.

        Parameters
        ----------
        time : jd
        '''

        unrounded = (time - self.transit_epoch)/self.period
        epoch =  np.round(unrounded)

        return epoch

    def findTransits(self, start, finish):

        '''
        Find all the available transits within a given time range.

        Parameters
        ----------

        start : float
            Start of the range, in jd.
        finish : float
            End of the range, in jd.

        Returns
        -------


        '''

        self.speak('finding transits for {0}'.format(self.name))
        self.transits = []

        # figure out the start and finish epochs
        begin, end = self.epoch(np.array([start, finish]))
        #print(start, finish)
        #print(begin, end)

        # populate a list of transit objects
        self.transits = np.array([Transit(self, i, plan=self.plan)
                                    for i in np.arange(begin, end+1)])

        self.speak('found {0} transits'.format(len(self.transits)))
    def filterTransits(self):
        '''
        Remove the transits that aren't observable.
        '''
        self.speak('excluding transits above airmass={0} or outside {1} twilight'.format(self.plan.maxairmass, self.plan.maxsun))

        # pull out the ingresses + egresses
        ingresses = [t.ingress for t in self.transits]
        egresses = [t.egress for t in self.transits]

        # start off assuming all transits are good
        ok = np.ones(len(self.transits)).astype(np.bool)

        # filter out the transits that start or end at too high of airmass
        for times in [ingresses, egresses]:

            # array of all the ingresses or all the egresses
            astropy_times = Time(times, format='jd')

            # figure out the object's altitude
            altaz = self.plan.observatory.altaz(self.coord, astropy_times)

            # exclude transits
            ok *= (altaz.alt.deg > 0) & (altaz.secz < self.plan.maxairmass)

            # filter out the transits that start or end when the Sun is up
            sunaltaz = self.plan.observatory.sun(astropy_times)
            ok *= sunaltaz.alt.deg < self.plan.maxsun

        self.transits = self.transits[ok]
        self.speak('filtered to {0} transits'.format(len(self.transits)))

    def plotTransits(self, **kw):
        kw['zorder'] = -self.stellar_distance
        for t in self.transits:
            t.plot(**kw)

    def __repr__(self):
        return f'<{self.name}, P={self.period}d, T0={self.transit_epoch}>'
