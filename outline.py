planets = {}
planets['wasp94b'] = {'name':'WASP94Ab', /
                      'ra_string':'20:55:07.94',	'dec_string':'-34:08:08.0' /
                      'ra':0.0,'dec':0.0, 'v:10.1, 	j:9.159, 	h:8.916, 	k:8.874, $
			period:3.950189, bjd:2456416.40116, duration:0.187, $
			period_uncertainty:0.000003, bjd_uncertainty:0.00026}
print_events, wasp94b, /lascamp, ndays=400, airmass=3.0


from zachopy.Talker import Talker

class Sample(Talker)
  ''
class Planet(Talker)

class Night(Talker)

class Observatory(Talker)
class ObservingRun(Talker)
