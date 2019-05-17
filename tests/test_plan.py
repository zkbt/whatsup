from whatsup import *
from exopop.Confirmed import Confirmed
from whatsup.imports import *

def speed(p):
    p.findTransits()
    p.printTransits()
    p.movieTransits()
    return p

def test_plan():

    # make the population
    c = Confirmed()
    bad = (c.depth < 0.01) | (c.distance > 50)

    c.removeRows(bad)

    # define the population
    p = Plan(pop=c)

    return speed(p)

#p.plotTransits()
#p.movie(filename='gj1132b_2016a.mp4')

if __name__ == '__main__':
    p = test_plan()
