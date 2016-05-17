from imports import *

from transit import Transit
from population import Interesting

class Planet(Interesting):
    def __init__(self, row, color='red', plan=None):
        Interesting.__init__(self, row)
        self.period = row['period']*astropy.units.day
        self.transit_epoch = astropy.time.Time(row['transit_epoch'], format='jd')
        self.color = color
        self.coord = astropy.coordinates.SkyCoord(self.ra*astropy.units.deg, self.dec*astropy.units.deg)
        self.plan = plan


    def epoch(self, time):
        unrounded = (astropy.time.Time(time) - self.transit_epoch)/self.period
        epoch =  np.round(unrounded)
        #midtransit = epoch*self.period + self.transit_epoch
        return epoch

    def findTransits(self, start, finish):
        self.speak('finding transits for {0}'.format(self.name))
        self.transits = []

        begin, end = self.epoch(np.array([start, finish]))
        n = (end - begin)
        for i in np.arange(n+1) + begin:
            self.transits.append(Transit(self, i, plan=self.plan))

        self.transits = np.array(self.transits)
        self.speak('found {0} transits'.format(len(self.transits)))

    def filterTransits(self):
        self.speak('excluding transits above airmass={0} or outside {1} twilight'.format(self.plan.maxairmass, self.plan.maxsun))
        ingresses = astropy.time.Time([t.ingress for t in self.transits])
        egresses = astropy.time.Time([t.egress for t in self.transits])
        #for i, t in enumerate(self.transits):
        #    t.airmasses = []
        #    t.sunalt = []

        # start off assuming all transits are good
        ok = np.ones(len(self.transits)).astype(np.bool)

        # filter out the transits that start or end at too high of airmass
        for times in [ingresses, egresses]:
            altaz = self.plan.observatory.altaz(self.coord, times)
            ok *= altaz.alt.deg > 0
            ok *= altaz.secz < self.plan.maxairmass
            #for i,t in enumerate(self.transits):
            #    t.airmasses.append(altaz.secz[i])


        # filter out the transits that start or end when the Sun is up
        for times in [ingresses, egresses]:
            sunaltaz = self.plan.observatory.sun(times)
            ok *= sunaltaz.alt.deg < self.plan.maxsun
            #for i,t in enumerate(self.transits):
            #    t.sunalt.append(sunaltaz.alt.deg[i])

        self.transits = self.transits[ok]
        self.speak('filtered to {0} transits'.format(len(self.transits)))

    def plotTransits(self, **kw):
        kw['zorder'] = -self.stellar_distance
        for t in self.transits:
            t.plot(**kw)
