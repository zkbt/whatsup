'''define a Transit class, to represent an individual planetary transit'''
from .imports import *

class Transit(Talker):
    '''a Transit object is one transit of one (associated) planet'''

    def __init__(self, planet, i, phasefrommidtransit=0.0, plan=None, buffer=3.0):
        '''
        initialize:
            planet = a Planet object (which contains a period and epoch)
            i = the epoch of this transit
            phasefrommidtransit = set this to 0.5 for eclipses from circular
            plan = the Plan object in which this is embedded
        '''

        # set up the talking
        Talker.__init__(self)

        # store lots of links to other objects
        self.planet = planet
        self.plan = plan
        self.observatory = self.plan.observatory

        # set the midtransit time of this particular transit
        self.midtransit = planet.period*(i + phasefrommidtransit) + planet.transit_epoch
        self.i = i

        # how much padding should be on the other side of the transit
        self.buffer = buffer

    @property
    def duration(self):
        '''the duration of the transit'''

        d = self.planet.duration
        try:
            d.unit
        except AttributeError:
            d = d*astropy.units.day

        if np.isfinite(d):
            return d
        else:
            return 5.0*astropy.units.hour # KLUDGE!

    @property
    def ingress(self):
        '''when is ingress?'''
        return self.midtransit - self.duration*(0.5)

    @property
    def egress(self):
        '''when is egress?'''
        return self.midtransit + self.duration*(0.5 )

    @property
    def pretransit(self):
        '''when should observations start?'''
        return self.ingress - self.duration*self.buffer

    @property
    def posttransit(self):
        '''when should observations end?'''

        return self.egress + self.duration*self.buffer

    @property
    def withbuffer(self):
        '''list of plot_date times from start to finish of observation'''
        return [self.pretransit.plot_date, self.posttransit.plot_date]

    @property
    def justtransit(self):
        '''list of plot_date times from start to finish of transit'''
        return [self.ingress.plot_date, self.egress.plot_date]

    def plot(self,  y=0, alpha=0.6, linewidth=5, marker=None, **kwargs):
        '''plot this transit within a night'''

        kwargs['marker'] = marker
        kwargs['linewidth'] = linewidth
        kwargs['alpha'] = alpha
        kwargs['color'] = self.planet.color

        # plot the transits
        vertical = [y,y]
        #self.plan.ax['transits'].plot(self.withself.buffer, vertical, **kwargs)
        #self.plan.ax['transits'].plot(self.justtransit, vertical,  **kwargs)
        # print self.planet.name, [self.pretransit.plot_date, self.posttransit.plot_date], [y,y]

        # plot the airmass
        times = self.pretransit + np.linspace(0, (self.buffer*2 + 1), 100)*self.duration
        altaz = self.plan.observatory.altaz(self.planet.coord, times)
        airmass = altaz.secz.value
        ok = altaz.alt > 0
        assert(self.duration < 0.5*astropy.units.day)

        intransit = (times >= self.ingress)*(times <= self.egress)

        self.plan.ax['airmass'].plot(times.plot_date[ok], airmass[ok], **kwargs)
        self.plan.ax['airmass'].plot(times.plot_date[ok*intransit], airmass[ok*intransit], **kwargs)

        self.plan.ax['transits'].text(self.midtransit.plot_date, y, self.planet.name, color=self.planet.color, ha='center', va='center', weight='bold', alpha=kwargs['alpha'], fontsize=5)

        #self.plan.ax['airmass'].set_ylim(self.plan.maxairmass, 0.9)
        self.plan.ax['airmass'].set_ylim(2.5, 0.9)

    def airmass(self, t):
        '''airmass string, for a particular time'''
        return '{0:.1f}'.format(self.observatory.altaz(self.planet.coord, t).secz.value)

    def sunalt(self, t):
        '''sunaltitude, for a particular time'''
        return '{0:+3.0f}'.format(self.observatory.sun(t).alt.deg)

    def simpletime(self, time):
        return '{0:.5f} = {1} UT (A={2},S={3})'.format( time.jd,
                                                time.iso[0:16],
                                                self.airmass(time),
                                                self.sunalt(time))

    def details(self):

        s  = "{0:<20s} [not accounting for heliocentric] \n".format(self.planet.name)
        s += " {0:3.1f}x duration before = {1}\n".format(self.buffer, self.simpletime(self.pretransit))
        s += "              ingress = {0}\n".format(self.simpletime(self.ingress))
        s += "          mid-transit = {0}\n".format(self.simpletime(self.midtransit))
        s += "               egress = {0}\n".format(self.simpletime(self.egress))
        s += "  {0:.1f}x duration after = {1}\n".format(self.buffer, self.simpletime(self.posttransit))

        print(s)
        return s
        #print('mid-transit = {0:.5f}  [{1} to {2} UT, secz = {3:.2f} to {4:.2f}, sun = {5:+3.0f} to {6:+3.0f}]'.format(

        #                    self.observatory.sun(t.pretransit).alt.deg,
        #                    self.observatory.sun(t.posttransit).alt.deg))
