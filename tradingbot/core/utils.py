
# -*- coding: utf-8 -*-

"""
tradingbot.core.utils
~~~~~~~~~~~~~~

This module provides utility functions that are used within tradinbot.
"""

# from decorator import decorate
import functools
from abc import ABCMeta, abstractmethod
from .logger import logger
from .data import pip_table


def _get_key(name, dicty):
    key = [x for x in dicty.keys() if x in name]
    if key:
        return dicty[key[0]]
    else:
        return False


def who_closest(target, val1, val2):
    """choose the closeset of two"""
    if abs(target - val1) < abs(target - val2):
        return val1
    else:
        return val2


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


# -~- Command Poll -~-
class CommandPoll(object):
    def __init__(self):
        self.poll = []
        self.results = []
        self.working = False

    def add(self, command, args=[], kwargs={}):
        self.poll.append([command, args, kwargs])
        if self.working is False:
            self.work()

    def work(self):
        self.working = True
        while self.poll:
            for func in self.poll:
                res = func[0](*func[1], **func[2])
                if res is not None:
                    self.results.append((func, res))
                self.poll.remove(func)
        self.working = False

    def get(self, command, args=[], kwargs={}):
        f = [command, args, kwargs]
        try:
            res = [x for x in self.results if x[0] == f][0]
            self.results.remove(res)
            return res[1]
        except Exception:
            raise


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


class Movement(object):
    def __init__(self, prod, quant=None, gain=None,
                 loss=None, mode=None, margin=None,
                 price=None):
        self.product = prod
        self.quantity = quant
        self.mode = mode
        self.gain = gain
        self.loss = loss
        self.margin = margin
        self.price = price

    def update(self, mov):
        self.quantity = mov.quantity
        self.earnings = mov.earn
        self.id = mov.id
