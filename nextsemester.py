import whatsup.plan as plan
from whatsup.imports import *
import numpy as np

p = plan.Plan(semester='2016A',  start='2016-01-01', finish='2016-07-31', maxairmass=2.5, maxsun=-6.0)


new = dict(name='GJ1132',
            period = 1.628930,
            transit_epoch = 2457184.55786,
            teff = 3270.0,
            stellar_radius=0.207,
            J = 9.245)
new['planet_radius'] = 1.16
new['rv_semiamplitude'] = None
new['planet_mass'] = 1.62
new['ra'] = 153.716025
new['dec'] = -47.15679722
new['b'] = 0.38
new['a_over_r'] = 16.0
p.known.standard.add_row(new)

transmission = p.known.standard
list = []
list.append(transmission[np.array(
            ['GJ1132' in name for name in transmission['name']])])
list.append(transmission[np.array(
            ['GJ1214' in name for name in transmission['name']])])
list.append(transmission[np.array(
            ['GJ3470' in name for name in transmission['name']])])
list.append(transmission[np.array(
            ['GJ436' in name for name in transmission['name']])])

list.append(transmission[np.array(
            ['GJ436' in name for name in transmission['name']])])

list.append(transmission[np.array(
            ['HIP116454' in name for name in transmission['name']])])

list.append(transmission[np.array(
            ['K2' in name for name in transmission['name']])])

list.append(transmission[np.array(
            ['WASP80' in name for name in transmission['name']])])
list.append(transmission[np.array(
            ['WASP94' in name for name in transmission['name']])])
list.append(transmission[np.array(
            ['HD189733' in name for name in transmission['name']])])
list.append(transmission[np.array(
            ['HD209458' in name for name in transmission['name']])])


#list.append(reflection[np.array(
#            ['WASP103' in name for name in reflection['name']])])


joined = astropy.table.vstack(list)

p.selectInteresting(table=joined)
p.findTransits()
p.printTransits()
p.plotTransits()
p.movie()
