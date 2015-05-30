import whatsup.plan as plan
from whatsup.imports import *
import numpy as np
import zachopy.units as units

p = plan.Plan('bathesheba', start='2015-05-01', finish='2015-07-15')


n = 30

new = dict(name='GJ1132',
            period = 1.62890221361,
            transit_epoch = 2456686.1110662,
            teff = 3200.0, # made up!
            stellar_radius=0.25, #made up!
            J = 9.245)
depth = 0.003
new['planet_radius'] = np.sqrt(depth)*new['stellar_radius']*units.Rsun/units.Rearth
new['rv_semiamplitude'] = None
new['planet_mass'] = None
new['ra'] = 153.716025
new['dec'] = -47.15679722
new['b'] = 0.5
duration = 0.03
new['a_over_r'] = new['period']/duration/np.pi
p.known.standard.add_row(new)






#joined = astropy.table.vstack([transmission, reflection])
list = ['GJ1132']



p.selectInteresting(list=list)
p.findTransits()
p.printTransits()
#p.plotTransits()
#p.movie()
