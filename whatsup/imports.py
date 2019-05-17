'''common modules to import'''

# zachopy contains lots of odds and ends
from craftroom.Talker import Talker
import thistothat, craftroom.strings, craftroom.units, craftroom.utils


import numpy as np, matplotlib.pyplot as plt
import astropy.units, astropy.time, astropy.coordinates, astropy.io.ascii, astropy.table

from astropy.time import Time
import astropy.units as u

from tqdm import tqdm

def clean(s):
    '''strip messy characters from a string'''
    new = s + ''
    for k in ' -!@#$%^&*':
        new = new.replace(k, '')
    return new
