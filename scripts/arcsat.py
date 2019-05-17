'''example script to show a list of nearby transits'''

import whatsup.plan as plan
from whatsup.imports import *
import numpy as np
from exopop.Confirmed import Confirmed

p = plan.Plan(observatory='APO', semester='2018-Q1',  start='2017-10-01', finish='2018-08-31', maxairmass=2.5, maxsun=-6.0)
p.population = Confirmed()


distance = 20
transmission = p.population.standard[p.population.distance < distance]
for i in range(len(transmission)):
    transmission['name'][i] =  transmission['name'][i] + ' (T)'

'''
p.selectInteresting(table=transmission)
p.findTransits()
p.printTransits()
p.plotTransits()
p.movie(filename='jaynetransits.mp4')
'''

#eclipses = p.population.standard[p.population.distance < distance]
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
p.printTransits()
p.plotTransits()
p.movie(filename='apo_fall.mp4')
