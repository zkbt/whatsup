from imports import *

class Semester(Talker):
    """
    The Semester object, for generating a sequence of nights.

    :param start:
        The start of the semester ()

    """
    def __init__(self, name='2015b', plan=None):
        Talker.__init__(self)
        self.plan = plan
        self.name = name
        if name == '2015B':
            start='2015-07-01'
            finish='2016-01-15'

        self.start, self.finish = astropy.time.Time([start, finish])
        self.midnights = astropy.time.Time(np.arange(self.start.jd, self.finish.jd), format='jd') + self.plan.observatory.standardzone
        resolution = 2*astropy.units.minute
        n = (self.finish - self.start + 2*astropy.units.day)/resolution
        self.times = self.start + np.arange(n)*resolution - 1*astropy.units.day
