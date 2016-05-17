import whatsup.plan as plan
from whatsup.imports import *
import numpy as np
from exopop.Confirmed import Confirmed

p = plan.Plan(semester='2016A',  start='2016-03-18', finish='2016-03-23', maxairmass=2.5, maxsun=-6.0)
p.known = Confirmed()

distance = 100.0
transmission = p.known.standard[np.array([p.known.find('WASP-19b')[0], p.known.find('GJ1132b')[0], p.known.find('WASP-43b')[0]])]
for i in range(len(transmission)):
    transmission['name'][i] =  transmission['name'][i] + ' (T)'

'''
p.selectInteresting(table=transmission)
p.findTransits()
p.printTransits()
p.plotTransits()
p.movie(filename='jaynetransits.mp4')
'''

eclipses = p.known.standard[p.known.find('WASP-43')]#p.known.distance < distance
for i in range(len(eclipses)):
    eclipses['name'][i] =  eclipses['name'][i] + ' (E)'
    eclipses['transit_epoch'][i] += eclipses['period'][i]/2.0

'''
p.selectInteresting(table=eclipses)
p.findTransits()
p.printTransits()
p.plotTransits()
p.movie(filename='jayneeclipses.mp4')
'''

combined = astropy.table.vstack([transmission, eclipses])
p.selectInteresting(table=combined)
p.findTransits()
p.printTransits()
p.plotTransits()
p.movie(filename='march21.mp4')
