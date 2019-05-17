'''example script to show a list of interesting transits'''

import whatsup.plan as plan
from whatsup.imports import *
import numpy as np

p = plan.Plan(name='transmission+reflection',  semester='2016A')


n = 100

trans = p.population.transmissionsignal/p.population.noisepertransit
goodfortransmission = np.argsort(trans)[::-1]
transmission = p.population.standard[goodfortransmission].copy()[:n]
for k in transmission:
    k['name'] += '(T)'

joined = transmission
if False:
    #joined = astropy.table.vstack([transmission, reflection])
    list = []
    list.append(transmission[np.array(
                ['GJ1214' in name for name in transmission['name']])])
    list.append(transmission[np.array(
                ['WASP80' in name for name in transmission['name']])])
    list.append(transmission[np.array(
                ['WASP94' in name for name in transmission['name']])])
    list.append(transmission[np.array(
                ['HD189733' in name for name in transmission['name']])])
    list.append(transmission[np.array(
                ['HD209458' in name for name in transmission['name']])])
    list.append(reflection[np.array(
                ['WASP103' in name for name in reflection['name']])])
    list.append(reflection[np.array(
                ['WASP18' in name for name in reflection['name']])])
    #list.append(reflection[np.array(
    #            ['WASP103' in name for name in reflection['name']])])

    joined = astropy.table.vstack(list)

p.selectInteresting(table=joined)
p.findTransits()
p.printTransits()
p.plotTransits()
p.movie()
