""" Base class for any effect """

class _Singleton(type):
    def __call__(cls, *args, **kwargs):
        try:
            return cls.__instance
        except AttributeError:
            cls.__instance = super(_Singleton, cls).__call__(*args, **kwargs)
            return cls.__instance

class Effect(metaclass=_Singleton):
    """ Base class to inherit from for effects """

    def __init__(self):
        self.time_step = 0

    def get_color(self, light=None):
        """ Return the color to display on the specified light for the current time step.

        light: The light for which to compute the color.
            (TODO: improve light to contain the vscan and hscan value)
        returns a 0. to 1. triple (r, g, b)
        """
        raise NotImplementedError('get_color function must be overridden in subclasses')

    def increment(self):
        """ Jump to next time step """
        self.time_step += 1

