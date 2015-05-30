import whatsup.plan as plan
from whatsup.imports import *
import numpy as np

p = plan.Plan(name='transmission+reflection')


n = 30

trans = p.known.transmissionsignal/p.known.noisepertransit
goodfortransmission = np.argsort(trans)[::-1]
transmission = p.known.standard[goodfortransmission].copy()[:n]
for k in transmission:
    k['name'] += '(T)'

refl = p.known.reflectionsignal/p.known.noisepertransit
goodforreflection = np.argsort(refl)[::-1]
reflection = p.known.standard[goodforreflection].copy()[:n]
for k in reflection:
    k['name'] += '(E)'
    k['transit_epoch'] += k['period']/2.0 # assuming e=0!


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
