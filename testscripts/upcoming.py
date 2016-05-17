import whatsup.plan as plan
from whatsup.imports import *
import numpy as np
import zachopy.units as units

p = plan.Plan('longer', start='2015-05-01', finish='2015-07-31')


n = 30

'''new = dict(name='GJ1132c',
            period = 8.98716607108,
            transit_epoch = 56690.2931839 + 2400000.5,
            teff = 3200.0, # made up!
            stellar_radius=0.2, #made up!
            J = 9.245)'''

new = dict(name='GJ1132c',
            period = 4.49378502693,
            transit_epoch = 56685.7847506 + 2400000.5,
            teff = 3200.0, # made up!
            stellar_radius=0.2, #made up!
            J = 9.245)
depth = 0.003
new['planet_radius'] = np.sqrt(depth)*new['stellar_radius']*units.Rsun/units.Rearth
new['rv_semiamplitude'] = None
new['planet_mass'] = None
new['ra'] = 153.716025
new['dec'] = -47.15679722
new['b'] = 0.5
duration = 0.04
new['a_over_r'] = new['period']/duration/np.pi
p.known.standard.add_row(new)






#joined = astropy.table.vstack([transmission, reflection])
list = ['GJ1132c']



p.selectInteresting(list=list)
p.findTransits()
p.printTransits()
p.plotTransits()
p.movie()
