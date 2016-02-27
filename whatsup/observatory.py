from imports import *

# create an empty dictionary
observatories = {}

# define a few observatories
#  parameters copied from skycalc.c source
observatories['CTIO'] = \
    dict(name="Cerro Tololo",
		timezone="Chilean",
		standardzone = 4.0*astropy.units.hour,
        usedaylightsaving = -1,
		longitude = 4.721*astropy.units.hourangle,
		latitude = -30.165*astropy.units.deg,
		elevsea = 2215.0*astropy.units.m,
		elev = 2215.0*astropy.units.m, # /* for ocean horizon, not Andes! */
	)

observatories['LCO'] = \
    dict(name="Las Campanas Observatory",
		timezone="Chilean",
		standardzone = 4.0*astropy.units.hour,
        usedaylightsaving = -1,
		longitude = 4.71333*astropy.units.hourangle,
		latitude = -29.00833*astropy.units.deg,
		elevsea = 2282.0*astropy.units.m,
		elev = 2282.0*astropy.units.m, # /* for ocean horizon, not Andes! */
	)

observatories['FLWO'] = \
    dict(name="Mt. Hopkins, AZ",
		timezone="Mountain",
		standardzone = 7.0*astropy.units.hour,
        usedaylightsaving = 0,
		longitude = 7.39233*astropy.units.hourangle,
		latitude = 31.6883*astropy.units.deg,
		elevsea = 2608.0*astropy.units.m,
		elev = 500.0*astropy.units.m, # /* approximate elevation above horizon mtns */
	)

class Observatory(Talker):
    """
    The Observatory object, for keeping track of timing calculating alt-az.

    :param name:
        String listing short name (LCO, CTIO, FLWO) of obsrvatory.

    """

    def __init__(self, abbreviation=None, plan=None):
        Talker.__init__(self)

        # make sure an abbreviation is defined
        if abbreviation is None:
            self.speak('Pick an observatory from following options:')
            self.speak(str(observatories.keys()))
            abbreviation = self.input().strip()

        o = observatories[abbreviation]
        for k in o.keys():
            self.__dict__[k] = o[k]

        self.location = astropy.coordinates.EarthLocation(lat=self.latitude,
                        lon=-self.longitude, height=self.elevsea)

        self.plan = plan

    def plotSun(self, times, ax=None, threshold=-12.0, color='black'):
        self.speak('plotting the sun')
        sunAltAz = self.sun(times)

        dt = times[1:] - times[:-1]
        nudged = times[:-1] + dt/2.0
        a = sunAltAz.alt.deg - threshold
        sunrises = ((a[1:] > 0)*(a[:-1] < 0)).nonzero()
        sunsets = ((a[1:] < 0)*(a[:-1] > 0)).nonzero()
        starts = nudged[sunrises]
        finishes = nudged[sunsets]
        maxlength = min(len(starts), len(finishes))
        if starts[0] > finishes[0]:
            starts, finishes = starts[:maxlength-1], finishes[1:maxlength]
        else:
            starts, finishes = starts[:maxlength], finishes[:maxlength]

        assert((finishes > starts).all())
        for i in range(len(starts)):
            ax.axvspan(starts[i].plot_date, finishes[i].plot_date, color=color, zorder=100)

    def sun(self, times):
        sunCoords = astropy.coordinates.get_sun(times)
        altAzFrame = astropy.coordinates.AltAz(obstime=times,
                        location=self.location)
        return sunCoords.transform_to(altAzFrame)

    def altaz(self, coord, times):
        frame = astropy.coordinates.AltAz(obstime=times, location=self.location)
        return coord.transform_to(frame)

    def plotAirmass(self, coord, times,  **kwargs):
        self.speak('plotting airmass')
        # calculate altaz
        altaz = self.altaz(coord, times)
        airmass = altaz.secz.value
        ok = altaz.alt > 0

        self.plan.ax['airmass'].plot(times.plot_date[ok], airmass[ok], **kwargs)
        self.plan.ax['airmass'].set_ylim(3,1)
