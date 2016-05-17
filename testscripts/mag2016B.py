import whatsup.plan as plan
from whatsup.imports import *
import numpy as np
from exopop.Confirmed import Confirmed

p = plan.Plan(semester='2016B',  start='2016-07-10', finish='2017-01-20', maxairmass=2.5, maxsun=-6.0)
p.known = Confirmed()

col = p.known.standard['name'].astype('S20')
p.known.standard.replace_column('name', col)

distance = 100.0
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
p.movie(filename='2016B.mp4')