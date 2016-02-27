from imports import *

class Semester(Talker):
    """
    The Semester object, for generating a sequence of nights.

    :param start:
        The start of the semester ()

    """
    def __init__(self, name='2015B', start=None, finish=None, plan=None):
        Talker.__init__(self)
        self.plan = plan
        self.name = name

        if start is not None and finish is not None:
            self.name = '{0}to{1}'.format(start, finish)
        else:
            if name == '2016A':
                start='2016-01-01'
                finish='2016-07-31'
            if name == '2015B':
                start='2015-07-01'
                finish='2016-01-15'
            if name == '2015A':
                start='2015-06-01'
                finish='2015-08-01'

            if name == '2014B':
                start='2014-07-01'
                finish='2015-01-15'

        self.start, self.finish = astropy.time.Time([start, finish])
        self.midnights = astropy.time.Time(np.arange(self.start.jd, self.finish.jd), format='jd') + self.plan.observatory.standardzone
        resolution = 10*astropy.units.minute
        n = (self.finish - self.start + 2*astropy.units.day)/resolution
        self.times = self.start + np.arange(n)*resolution - 1*astropy.units.day
