
# -*- coding: utf-8 -*-

"""
tradingbot.core.utils
~~~~~~~~~~~~~~

This module provides utility functions that are used within tradinbot.
"""

from .logger import logger
from .data import pip_table


def __get_key(name, dicty):
    key = [x for x in dicty.keys() if x in name]
    if key:
        return dicty[key[0]]
    else:
        return False


def _close_to(val1, val2, swap):
    """check if val1 is around val2 by swap"""
    if val2 - swap < val1 and val1 < val2 + swap:
        return True
    else:
        return False


def _conv_limit(gain, loss, name):
    """convert pip from natural numbers
     to corresponding float number"""
    pip = __get_key(name, pip_table)
    if pip is False:
        logger.warning(f"limit not converted for {name}")
        raise
    gain *= pip
    loss *= pip
    return gain, loss


# -~- Momoize -~-
class Memoize:
    def __init__(self, fn):
        self.fn = fn
        self.memo = {}

    def __call__(self, *args):
        if args not in self.memo:
            self.memo[args] = self.fn(*args)
        return self.memo[args]


# -~- API supplements -~-
class ApiSupp(object):
    def __init__(self, api):
        self.api = api

    @Memoize
    def get_unit_value(self, name):
        if self.api.open_mov(name):
            try:
                pip = __get_key(name, pip_table)
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
