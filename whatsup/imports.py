'''common modules to import'''

from zachopy.Talker import Talker
import numpy as np, matplotlib.pyplot as plt
import zachopy.relations, zachopy.strings, zachopy.units, zachopy.utils
import astropy.units, astropy.time, astropy.coordinates, astropy.io.ascii, astropy.table

def clean(s):
    '''strip messy characters from a string'''
    return s.translate(None, ' -!@#$%^&*')
