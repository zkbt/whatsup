# -*- coding: utf-8 -*-

# set the version number for this package
__version__ = "0.1.0"

# this is something sneaky to make this file callable from within setup.py
#   (to determine the version number)
try:
    __WHATSUP_SETUP__
except NameError:
    __WHATSUP_SETUP__ = False

# is this is any import other than during installation?
if not __WHATSUP_SETUP__:

    # these are the only things that can be called straight from this level
    __all__ = [
        "Night", "Observatory", "Planet", "population", "Transit"
    ]

    # import these class definitons, so they can be called directly as like
    #   p = whatsup.Planet()

    from .night import Night
    from .observatory import Observatory
    from .planet import Planet
    from .transit import Transit
    from . import population
