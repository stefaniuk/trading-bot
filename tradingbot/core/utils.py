
# -*- coding: utf-8 -*-

"""
tradingbot.core.utils
~~~~~~~~~~~~~~

This module provides utility functions that are used within tradinbot.
"""

# from decorator import decorate
import functools
from .logger import logger
from .data import pip_table


def _get_key(name, dicty):
    key = [x for x in dicty.keys() if x in name]
    if key:
        return dicty[key[0]]
    else:
        return False


def close_to(val1, val2, swap):
    """check if val1 is around val2 by swap"""
    if val2 - swap < val1 and val1 < val2 + swap:
        return True
    else:
        return False


def conv_limit(gain, loss, name):
    """convert pip from natural numbers
     to corresponding float number"""
    pip = _get_key(name, pip_table)
    if pip is False:
        logger.warning(f"limit not converted for {name}")
        raise
    gain *= pip
    loss *= pip
    return gain, loss


# -~- Momoize -~-
# def _memoize(func, *args, **kw):
#     if kw:  # frozenset is used to ensure hashability
#         key = args, frozenset(kw.items())
#     else:
#         key = args
#     cache = func.cache  # attribute added by memoize
#     if key not in cache:
#         cache[key] = func(*args, **kw)
#     return cache[key]
#
#
# def memoize(f):
#     """
#     A simple memoize implementation. It works by adding a .cache dictionary
#     to the decorated function. The cache will grow indefinitely, so it is
#     your responsibility to clear it, if needed.
#     """
#     f.cache = {}
#     return decorate(f, _memoize)

# class memoize(object):
#     def __init__(self, func):
#         self.func = func
#         self.cache = {}
#
#     def __get__(self, obj, objtype):
#         '''Support instance methods.'''
#         return functools.partial(self.__call__, obj)
#
#     def __call__(self, *args):
#         if args in self.cache:
#             return self.cache[args]
#         else:
#             value = self.func(*args)
#             self.cache[args] = value
#             return value


# -~- API supplements -~-
class ApiSupp(object):
    def __init__(self, api):
        self.api = api

    @functools.lru_cache()
    def get_unit_value(self, name):
        """get unit value of stock based on margin"""
        if self.api.open_mov(name):
            try:
                pip = _get_key(name, pip_table)
                if pip is False:
                    raise
                quant = 1 / pip
                self.api.set_quantity(quant)
                margin = self.api.get_mov_margin()
            except Exception:
                logger.error(f"failed to get margin of {name}")
                raise
            finally:
                self.api.close_mov()
            return margin / quant
