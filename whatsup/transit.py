from imports import *
buffer = 1.0

class Transit(Talker):
    def __init__(self, planet, i, phasefrommidtransit=0.0, plan=None):
        Talker.__init__(self)
        self.planet = planet
        self.midtransit = planet.period*(i + phasefrommidtransit) + planet.transit_epoch
        self.i = i
        self.plan = plan
        self.observatory = self.plan.observatory


    @property
    def duration(self):
        return self.planet.duration

    @property
    def ingress(self):
        return self.midtransit - self.duration*(0.5)

    @property
    def egress(self):
        return self.midtransit + self.duration*(0.5 )

    @property
    def pretransit(self):
        return self.ingress - self.duration*buffer

    @property
    def posttransit(self):
        return self.egress + self.duration*buffer

    @property
    def withbuffer(self):
        return [self.pretransit.plot_date, self.posttransit.plot_date]

    @property
    def justtransit(self):
        return [self.ingress.plot_date, self.egress.plot_date]

    def plot(self,  y=0, alpha=0.75, linewidth=10, marker=None, **kwargs):

        kwargs['marker'] = marker
        kwargs['linewidth'] = linewidth
        kwargs['alpha'] = alpha
        kwargs['color'] = self.planet.color

        # plot the transits
        vertical = [y,y]
        #self.plan.ax['transits'].plot(self.withbuffer, vertical, **kwargs)
        #self.plan.ax['transits'].plot(self.justtransit, vertical,  **kwargs)
        print self.planet.name, [self.pretransit.plot_date, self.posttransit.plot_date], [y,y]

        # plot the airmass
        times = self.pretransit + np.linspace(0, (buffer*2 + 1)*self.duration, 100)
        altaz = self.plan.observatory.altaz(self.planet.coord, times)
        airmass = altaz.secz.value
        ok = altaz.alt > 0

        intransit = (times >= self.ingress)*(times <= self.egress)

        self.plan.ax['airmass'].plot(times.plot_date[ok], airmass[ok], **kwargs)
        self.plan.ax['airmass'].plot(times.plot_date[ok*intransit], airmass[ok*intransit], **kwargs)

        self.plan.ax['transits'].text( self.midtransit.plot_date, y, self.planet.name, color=self.planet.color, ha='center', va='center', weight='bold', alpha=kwargs['alpha'])

        #self.plan.ax['airmass'].set_ylim(self.plan.maxairmass, 0.9)
        self.plan.ax['airmass'].set_ylim(3, 0.9)

    def airmass(self, t):
        return '{0:.1f}'.format(self.observatory.altaz(self.planet.coord, t).secz.value)

    def sunalt(self, t):
        return '{0:+3.0f}'.format(self.observatory.sun(t).alt.deg)

    def simpletime(self, time):
        return '{0:.5f} = {1} UT (A={2},S={3})'.format( time.jd,
                                                time.iso[0:16],
                                                self.airmass(time),
                                                self.sunalt(time))

    def details(self):

        s  = "{0:<20s} [not accounting for heliocentric] \n".format(self.planet.name)
        s += " {0:3.1f}x duration before = {1}\n".format(buffer, self.simpletime(self.pretransit))
        s += "              ingress = {0}\n".format(self.simpletime(self.ingress))
        s += "          mid-transit = {0}\n".format(self.simpletime(self.midtransit))
        s += "               egress = {0}\n".format(self.simpletime(self.egress))
        s += "  {0:.1f}x duration after = {1}\n".format(buffer, self.simpletime(self.posttransit))

        print s
        #print('mid-transit = {0:.5f}  [{1} to {2} UT, secz = {3:.2f} to {4:.2f}, sun = {5:+3.0f} to {6:+3.0f}]'.format(

        #                    self.observatory.sun(t.pretransit).alt.deg,
        #                    self.observatory.sun(t.posttransit).alt.deg))
