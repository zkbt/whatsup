'''example script to show one particular transiting planet'''

import whatsup.plan as plan
from whatsup.imports import *
import numpy as np
from exopop.Confirmed import Confirmed

p = plan.Plan(semester='2016A',  start='2016-12-20', finish='2016-12-30', maxairmass=2.5, maxsun=-6.0)
p.known = Confirmed()

distance = 100.0
transmission = p.known.standard[np.array([p.known.find('GJ1132b')[0]])]
for i in range(len(transmission)):
    transmission['name'][i] =  transmission['name'][i] + ' (T)'

p.selectInteresting(table=transmission)
p.findTransits()
p.printTransits()
p.plotTransits()
p.movie(filename='gj1132b_2016a.mp4')
