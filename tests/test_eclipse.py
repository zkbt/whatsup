from whatsup import *
from exopop.Confirmed import Confirmed
from whatsup.imports import *
import copy

c = Confirmed()

# make the population
transits = copy.deepcopy(c)

# remove everything beside KELT-16b
transits.removeRows(transits.name != 'KELT-16b')
for i in range(len(transits.standard)):
    transits.standard[i]['name'] += ' (T)'
transits

eclipses = copy.deepcopy(c)
eclipses.removeRows(eclipses.name != 'KELT-16b')
for i in range(len(eclipses.standard)):
    eclipses.standard[i]['name'] += ' (E)'
    eclipses.standard[i]['transit_epoch'] += eclipses.standard[i]['period']/2.0
eclipses

# define the population
p = Plan(observatory='APO',
        start=Time('2019-7-01', format='iso'),
        finish=Time('2019-10-01', format='iso'),
        pop=eclipses,
        maxairmass=2.5)

p.findTransits()
p.printTransits()
p.movieTransits()
#p.plotTransits()
#p.movie(filename='gj1132b_2016a.mp4')
