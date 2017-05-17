'''example script to show a list of nearby transits'''

import whatsup.plan as plan
from whatsup.imports import *
import numpy as np
from exopop.Confirmed import Confirmed

p = plan.Plan(observatory='APO', semester='2017-Q3',  start='2016-07-01', finish='2016-09-30', maxairmass=2.5, maxsun=-6.0)
p.known = Confirmed()

col = p.known.standard['name'].astype('S20')
p.known.standard.replace_column('name', col)

distance = 100
transmission = p.known.standard[p.known.distance < distance]
for i in range(len(transmission)):
    transmission['name'][i] =  transmission['name'][i] + ' (T)'

'''
p.selectInteresting(table=transmission)
p.findTransits()
p.printTransits()
p.plotTransits()
p.movie(filename='jaynetransits.mp4')
'''

#eclipses = p.known.standard[p.known.distance < distance]
#for i in range(len(eclipses)):
#    eclipses['name'][i] =  eclipses['name'][i] + ' (E)'
#    eclipses['transit_epoch'][i] += eclipses['period'][i]/2.0

'''
p.selectInteresting(table=eclipses)
p.findTransits()
p.printTransits()
p.plotTransits()
p.movie(filename='jayneeclipses.mp4')
'''

#combined = astropy.table.vstack([transmission, eclipses])
combined = transmission
p.selectInteresting(table=combined)
p.findTransits()
#p.printTransits()
p.plotTransits()
p.movie(filename='apo_summer.mp4')
