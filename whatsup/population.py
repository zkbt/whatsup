from imports import *

mamajek = zachopy.relations.Mamajek()

class Population(Talker):
    def __init__(self, **kwargs):
        Talker.__init__(self, **kwargs)
        self.load()
        self.trim()
        self.loadStandard()

    def loadStandard(self):
        filename = 'standardized_' + self.filename
        try:
            self.standard = astropy.table.Table(np.load(filename))
        except:
            self.createStandard()
            np.save(filename, self.standard)
        self.propagate()

    def propagate(self):
        for k in self.standard.colnames:
            self.__dict__[k] = self.standard[k]


    def find(self, name):
        def clean(s):
            for junk in [' ','-']:
                s = s.replace(junk, '')
            return s
        return np.array([clean(name) in clean(x) for x in self.name]).nonzero()[0]

    def __str__(self):
        print self.standard
        return ''

    @property
    def n(self):
        return len(self.standard)
    @property
    def filename(self):
        return self.__class__.__name__ + '.npy'

    @property
    def absoluteJ(self):
        # use the effective temperature to select a J-band bolometric correction, then

        # pull out a proxy for the Sun from the Mamajek table
        sun = mamajek.table[mamajek.table['SpT'] == 'G2V']

        # figure out the bolometric luminosities
        teffratio = self.teff/sun['Teff']
        radiusratio = self.stellar_radius
        luminosities = teffratio**4*radiusratio**2

        # figure out the absolute J magnitude of a dwarf with this teff
        dwarf_absolutej = mamajek.tofrom('M_J')('Teff')(self.teff.data)

        # figure out how bright a dwarf star of the same effective temperature would be
        dwarf_luminosities = 10**mamajek.tofrom('logL')('Teff')(self.teff.data)

        # figure out how much brighter this star is than its Teff-equivalent dwarf
        ratio = luminosities/dwarf_luminosities
        return dwarf_absolutej - 2.5*np.log10(ratio)

    @property
    def distance(self):
        try:
            return self.standard['distance']
        except:
            return 10**(1 + 0.2*(self.J - self.absoluteJ))

    @property
    def teq(self):
        try:
            return self.standard['teq']
        except:
            return self.teff/np.sqrt(2*self.a_over_r)


    @property
    def duration(self):
        return self.period/np.pi/self.a_over_r

    @property
    def photons(self):
        return 10**(-0.4*self.J)

    @property
    def surfacegravity(self):
        try:
            self.planet_mass
        except:
            return 1000.0
        g = zachopy.units.G*self.planet_mass*zachopy.units.Mearth/(self.planet_radius*zachopy.units.Rearth)**2
        g[g <= 0] = 2000.0
        return g

        # for comparing with mass-less planets!

    @property
    def mu(self):
        # for comparing planets of different compositions
        return 2.32

    @property
    def scaleheight(self):
        return zachopy.units.k_B*self.teq/self.mu/zachopy.units.mp/self.surfacegravity

    @property
    def noisepertransit(self):
        return 1.0/np.sqrt(self.photons*self.duration)

    @property
    def noisepertime(self):
        return 1.0/np.sqrt(self.photons/self.a_over_r)

    @property
    def transmissionsignal(self):
        return 2*self.scaleheight*self.planet_radius/self.stellar_radius**2

    @property
    def emissionsignal(self):
        return (self.planet_radius/self.stellar_radius)**2*self.teq/self.teff

    @property
    def reflectionsignal(self):
        return self.depth/self.a_over_r**2


    @property
    def cheopsnoisepertransit(self):
        #150 ppm/min for a 9th magnitude star (in V)
        cheopsnoiseperminute =  150.0/1e6/np.sqrt(10**(-0.4*(self.V - 9.0)))
        durationinminutes = self.duration*24.0*60.0
        return cheopsnoiseperminute/np.sqrt(durationinminutes)


    @property
    def depth(self):
        return (self.planet_radius*zachopy.units.Rearth/self.stellar_radius/zachopy.units.Rsun)**2

    def plot(self, xname, yname, names=True, xlog=True, ylog=True):
        plt.ion()
        x, y = self.standard[xname], self.standard[yname]
        try:
            self.ax.cla()
        except:
            self.figure = plt.figure('Exoplanet Population')
            self.ax = plt.subplot()
        self.ax.set_xlabel(xname)
        self.ax.set_ylabel(yname)
        self.ax.plot(x, y, marker='o', alpha=0.5, color='gray', linewidth=0)
        if False:
            for i in range(len(x)):
                self.ax.text(x[i], y[i], self.table['NAME'][i])
        if xlog:
            plt.xscale('log')
        if ylog:
            plt.yscale('log')

        plt.draw()

    def thumbtack(self, maxr=1000, dr=100, labels=False):
        def scale(d):
            return np.array(d)**1.5
        r = scale(self.distance)
        x, y = r*np.cos(self.ra*np.pi/180), r*np.sin(self.ra*np.pi/180)
        plt.ion()
        plt.figure('thumbtacks')

        ax = plt.subplot()
        ax.cla()
        ax.set_aspect('equal')
        theta = np.linspace(0,2*np.pi,1000)
        angle = -90*np.pi/180

        gridkw = dict(alpha=0.25,  color='green')
        for originalradius in np.arange(dr,maxr*2,dr):
            radii = scale(originalradius)

            ax.plot(radii*np.cos(theta), radii*np.sin(theta), linewidth=3, **gridkw)
            ax.text(radii*np.cos(angle), radii*np.sin(angle), '{0:.0f} pc'.format(originalradius), rotation=90+ angle*180/np.pi, va='bottom', ha='center', size=13, weight='extra bold', **gridkw)

        ax.plot(x, y, marker='o', alpha=0.5, color='gray', linewidth=0, markeredgewidth=0)
        close = (self.name == 'WASP-94A b').nonzero()[0]#(self.distance < maxr).nonzero()[0]
        if labels:
            for c in close:
                plt.text(x[c], y[c], self.name[c])
        ax.set_xlim(-scale(maxr), scale(maxr))
        ax.set_ylim(-scale(maxr), scale(maxr))

        #self.input('add TESS?')
        #ax.plot(tx, ty, marker='o', alpha=0.5, color='red', linewidth=0, markeredgewidth=0)

        '''n = 10000
        x, y, z = np.random.uniform(-1000,1000, n),  np.random.uniform(-1000,1000, n),  np.random.uniform(-1000,1000, n)
        ra = np.arctan2(y,x)
        r = np.sqrt(x**2 + y**2 + z**2)
        ok = (r<1000)*(r>500)
        rescale = (scale(r)/r)[ok]
        plt.plot(scale(r)[ok]*np.cos(ra[ok]), scale(r)[ok]*np.sin(ra[ok]), color='black', marker='o', linewidth=0)
        plt.draw()'''


    def compare(self, x='teq', y='radius', area='depth', color='stellar_radius'):

        xplot = self.__dict__[x]
        yplot = self.__dict__[y]
        sizeplot = self.__dict__[size]
        colorplot = self.__dict__[color]

        maxarea = 1000
        area = self.__dict__[area]
        sizeplot = np.sqrt(area/np.nanmax(area)*maxarea)

        plt.scatter(xplot, yplot, linewidth=0, marker='o', markersize=sizeplot)


class Known(Population):
    def __init__(self):
        '''Initialize a population of simulated TESS planets, from Peter Sullivan's simulations.'''
        Population.__init__(self)

    def load(self):

        try:
            self.table = astropy.table.Table(np.load(self.filename))
            self.speak('loaded pre-saved known exoplanet population')
        except:
            self.table = astropy.io.ascii.read('exoplanets.csv')
            np.save(self.filename, self.table)
            self.speak('loaded known exoplanet population and re-saved it to {0}'.format(self.filename))

            # report original size
            self.speak('original table contains {0} elements'.format(len(self.table)))

            # trim non-transiting
            good = self.table['TRANSIT'] == 1
            self.table = self.table[good]
            self.speak('trimmed to {0} transiting planets'.format(np.sum(good)))

            # trim ones with bad parameters
            good = (self.table['TEFF'] > 0) * (self.table['RSTAR'] > 0) * (self.table['J'] > 0.0)
            self.speak('trimmed to {0} systems with good Teff, stellar radius, or J magnitude'.format(np.sum(good)))
            self.table = self.table[good]

            # merge to pull KOI information as needed
            '''self.speak('trying to merge with the KOI list')

            for i in range(len(self.table))[::-1]:
                if ('KOI' in self.table['NAME'][i]):
                    try:
                        match = np.nonzero(self.kois['kepid'] == self.table[i]['KEPID'])[0][0]
                        self.speak('want to replace {0} with {1}'.format(self.table[i]['NAME'], self.kois[match]['kepoi_name'].data))
                        oldpositions = self.table[i]['RA_STRING'], self.table[i]['DEC_STRING']
                        newpositions = self.kois[match]['ra_str'], self.kois[match]['dec_str']
                        self.speak('{0} to {1}'.format(oldpositions, newpositions))
                        self.table[i]['RA_STRING'], self.table[i]['DEC_STRING'] = newpositions
                        if self.kois[match]['koi_disposition'] == 'FALSE POSITIVE':
                            self.table.remove_row(i)
                            self.speak('FALSE POSITIVE! table is now {0} rows long'.format(len(self.table)))
                    except:
                        pass
                        #self.speak("couldn't find match for {0}".format(self.table['NAME'][i]))

            # convert the RA and Dec strings into positions
            self.convert()'''
            #np.save('merged.npy', self.table)
        #include = (self.table['TRANSIT' == 1])&(self.table['PER'] < 1000)&(self.table['R'] < 10)
        #self.table = self.table[include]

    def trim(self):
        ok = self.table['B'] < (1.0 - self.table['RR'])
        ok *= self.table['J'] != 0.0
        ok *= self.table['TRANSIT'] == 1
        ok *= self.table['TEFF'] > 0
        ok *= np.array(['Kepler' not in x for x in self.table['NAME']])
        ok *= np.array(['KOI' not in x for x in self.table['NAME']])
        ok *= np.array(['KIC' not in x for x in self.table['NAME']])
        self.trimmed = self.table[ok]

    def createStandard(self):
        t = self.trimmed
        s = astropy.table.Table()
        s['name'] = t['NAME']
        #s['kepid'] = 'KEPID'
        s['period'] = t['PER']
        s['transit_epoch'] = t['TT']
        s['teff'] = t['TEFF']
        s['stellar_radius'] = t['RSTAR']
        s['J'] = t['J']
        s['planet_radius'] = t['R']*zachopy.units.Rjupiter/zachopy.units.Rearth
        s['a_over_r'] = t.MaskedColumn(t['AR'], mask=t['AR']==0.0)
        #s['teq'] = 280.0*t['S/Se']**0.25
        s['rv_semiamplitude'] =  t.MaskedColumn(t['K'], mask=t['K']==0.0)
        s['planet_mass'] = t['MASS']*zachopy.units.Mjupiter/zachopy.units.Mearth
        s['radius_ratio'] = t['RR']
        badpos = (t['RA'] ==0.0)*(t['DEC'] == 0.0)
        s['ra'] = t.MaskedColumn(t['RA']*15.0, mask=badpos)
        s['dec'] = t.MaskedColumn(t['DEC'], mask=badpos)
        s['b'] = t['B']
        self.standard = s
        '''self.standard.add_row(dict(name='WASP-94A b', period=3.9501907,             transit_epoch=2456416.39659,
                                teff=6153.0, stellar_radius=1.62, J=9.159,
                                planet_radius=1.72*zachopy.units.Rjupiter/zachopy.units.Rearth,
                                a_over_r=7.3488, planet_mass=0.452*zachopy.units.Mjupiter/zachopy.units.Mearth,
                                radius_ratio=0.109, b=0.17,
                                ra=313.78308, dec=-34.135528))'''


class TESS(Population):
    def __init__(self):
        '''Initialize a population of simulated TESS planets, from Peter Sullivan's simulations.'''
        Population.__init__(self)
        self.createStandard()

    def load(self, remake=False):
        try:
            assert(remake==False)
            self.table = astropy.table.Table(np.load(self.filename))
            self.speak('loaded pre-saved TESS simulated population')
        except:
            self.table = astropy.io.ascii.read('tess_sim.cat')
            np.save(self.filename, self.table)
            self.speak('loaded TESS simulated population and re-saved it to {0}'.format(self.filename))

    def trim(self):
        self.trimmed = self.table

    def createStandard(self):
        t = self.trimmed
        s = astropy.table.Table()
        s['name'] = ['tess{0:04}i'.format(i) for i in range(len(t))]
        s['kepid'] = None
        s['period'] = t['P/day']
        s['teff'] = t['Teff[K]']
        s['stellar_radius'] = t['Rs/Rsun']
        s['J'] = t['J']
        s['V'] = t['V']

        s['planet_radius'] = t['Rp/Re']

        s['teq'] = 280.0*t['S/Se']**0.25
        s['a_over_r'] = 0.5*(s['teff']/s['teq'])**2
        s['rv_semiamplitude'] = t['RV[m/s]']
        s['radius_ratio'] = t['Rp/Re']*zachopy.units.Rearth/(t['Rs/Rsun']*zachopy.units.Rsun)
        s['distance'] = 10*10**(0.2*t['DM'])
        s['ra'] = t['RA/deg']
        s['dec'] = t['DEC/deg']

        self.standard = s


class KOI(Population):
    def __init__(self):
        '''Initialize a population of KOIs, from the downloaded CSV.'''
        Population.__init__(self)

    def load(self):
        try:
            self.table = astropy.table.Table(np.load(self.filename))
            self.speak('loaded pre-saved KOI  population')
        except:
            self.table = astropy.io.ascii.read('kois.csv')
            np.save(self.filename, self.table)
            self.speak('loaded KOI population and re-saved it to {0}'.format(self.filename))

        for k in self.table.colnames:
            if 'koi_' in k:
                self.table[k].name = k.replace('koi_', '')

        for i in range(len(self.table['kepler_name'])):
            if 'Kepler-444' in self.table['kepler_name'][i]:
                print 'REPLACING!'
                self.table['srad'][i] = 0.752

        fromexoorg = Known().table[['KEPID','J']].group_by('KEPID').groups.aggregate(np.mean)
        fromexoorg['KEPID'].name = 'kepid'
        self.table = astropy.table.join(fromexoorg,self.table, 'kepid')

    def trim(self):
        cut = self.table['disposition'] != 'FALSE POSITIVE'
        cut *= self.table['impact'] <= (1.0 - self.table['ror'])
        cut *= self.table['srad'] <= (4.0)
        cut *= self.table['steff'] > 0
        self.trimmed = self.table[cut]#astropy.table.Table(np.unique(self.table[cut]))

    def createStandard(self):

        t = self.trimmed
        s = astropy.table.Table()
        s['name'] = t.MaskedColumn(t['kepler_name'], mask=t['kepler_name']!='0')
        s['kepid'] = t['kepid']
        s['period'] = t['period']
        s['teff'] = t['steff']
        s['stellar_radius'] = t['srad']

        s['J'] = t['J']
        s['planet_radius'] = t['prad']
        s['a_over_r'] = 0.5*(s['teff']/t['teq'])**2
        s['radius_ratio'] = t['ror']
        s['b'] = t['impact']

        ras, decs = [],[]
        for i in range(len(t)):
            ra, dec = zachopy.strings.unclockify(t[i]['ra_str'] + ' ' + t[i]['dec_str'])
            ras.append(ra)
            decs.append(dec)

        s['ra'] = ras
        s['dec'] = decs



        self.standard = s[s['teff'] > 0]


class Interesting(Population):
    """
    The Interesting object, for keeping track planets worth observing.
    """
    def __init__(self, filtered):
        Talker.__init__(self)
        # don't do the default Population initialization
        self.standard = filtered
        self.propagate()
