# -*- coding: utf-8 -*-

"""
tradingbot.core.utils
~~~~~~~~~~~~~~

This module provides utility functions that are used within tradinbot.
"""

# from decorator import decorate
import time
import functools
from abc import ABCMeta, abstractmethod
from threading import Thread
from .color import *
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


def eval_earn(quant, curr, price, mode):
    """evaluate earnings"""
    if mode == 'buy':
        diff = curr - price
    else:
        diff = price - curr
    earnings = str(round(diff * quant, 2))
    if diff > 0:
        return green(earnings)
    elif diff < 0:
        return red(earnings)
    else:
        return earnings


# -~- Command Pool -~-
class CommandPool(object):
    def __init__(self):
        self.pool = []
        self.results = []
        self.working = False

    def check_add(self, command, args=[], kwargs={}):
        cmd = [command, args, kwargs]
        if cmd in self.pool:
            return False
        else:
            self.add(command, args, kwargs)
            return False

    def add(self, command, args=[], kwargs={}):
        self.pool.append([command, args, kwargs])
        if self.working is False:
            Thread(target=self.work).start()

    def wait(self, command, args=[], kwargs={}, timeout=30):
        for _ in range(timeout):
            try:
                return self.get(command, args, kwargs)
            except Exception as e:
                exc = e
                time.sleep(1)
        raise exc

    def add_and_wait_single(self, command, args=[], kwargs={}, timeout=30):
        self.check_add(command, args, kwargs)
        return self.wait(command, args, kwargs, timeout)

    def add_and_wait(self, command, args=[], kwargs={}, timeout=30):
        self.add(command, args, kwargs)
        return self.wait(command, args, kwargs, timeout)

    def work(self):
        self.working = True
        while self.pool:
            for func in self.pool:
                res = func[0](*func[1], **func[2])
                if res is not None:
                    self.results.append((func, res))
                self.pool.remove(func)
        self.working = False

    def get(self, command, args=[], kwargs={}):
        f = [command, args, kwargs]
        try:
            res = [x for x in self.results if x[0] == f][0]
            self.results.remove(res)
            return res[1]
        except Exception:
            raise


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
        self.id = None

    def update(self, mov):
        self.curr = mov.curr
        self.price = mov.price
        self.quantity = mov.quantity
        self.id = mov.id
