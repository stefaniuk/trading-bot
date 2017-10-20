# -*- coding: utf-8 -*-

"""
tradingbot.core.algorithm
~~~~~~~~~~~~~~

This module define algorithm's abstract class and calculator.
"""

import time
import os.path
import abc
from threading import Thread
from ..patterns import Observer
from ..glob import Glob
# from .handler import Handler

# logging
import logging
logger = logging.getLogger('tradingbot.algorithm')


class Calculator(object):
    """namespace for complex predictive functions (buy conventionally)"""
    def __init__(self, p_stock):
        self.product = p_stock.product
        self.stock = p_stock.candle
        self.k_fast_list = []
        self.k_list = []
        self.emas = {}

    def _clear(self):
        """avoid memory overload"""
        for key in self.emas.keys():
            self.emas[key] = self.emas[key][-50:]

    def sma(self, periods):
        """calculate the Simple Moving Average"""
        records = self.stock.records
        close_list = [x[1][-1] for x in records[-periods:]]
        return sum(close_list) / len(close_list)

    def ema(self, periods):
        """calculate the Exponential Moving Average"""
        # instantiate ema of given period in self.emas
        if periods not in self.emas.keys():
            self.emas[periods] = []
        records = self.stock.records
        close = records[-1][1][-1]
        multiplier = 2 / (periods + 1)
        if len(self.emas[periods]) == 0:
            latest_ema = close
        else:
            latest_ema = self.emas[periods][-1]
        ema = (close - latest_ema) * multiplier + latest_ema
        self.emas[periods].append(ema)
        # clear up
        self._clear()
        return ema

    def stochastic_oscillator(self, k_period, k_slow_period, d_period):
        """calculate the Stochastic Oscillator 5 3 3"""
        records = self.stock.records[-k_period:]
        close = records[-1][1][-1]
        highest_high = max([x[1][1] for x in records])
        lowest_low = min([x[1][2] for x in records])
        k_fast = (close - lowest_low) / (highest_high - lowest_low) * 100
        self.k_fast_list.append(k_fast)
        self.k_fast_list = self.k_fast_list[-k_slow_period:]
        k = sum(self.k_fast_list) / len(self.k_fast_list)
        self.k_list.append(k)
        self.k_list = self.k_list[-d_period:]
        d = sum(self.k_list) / len(self.k_list)
        return d


class BaseAlgorithm(Observer, metaclass=abc.ABCMeta):
    """abstract class for all algorithms"""
    def __init__(self):
        super().__init__()
        self.register_obs(Glob().recorder)
        self.strategy = Glob().collection['strategy']
        # handle errors
        if not hasattr(Glob(), 'recorder'):
            raise NotImplementedError("need to implement recorder")
        if not hasattr(Glob(), 'handler'):
            raise NotImplementedError("need to implement handler")
        self.stocks = []

    def start(self, sleep_time=0):
        """start the handlers and the run function"""
        Thr = Thread(target=self.run, args=(sleep_time,))
        Thr.deamon = True
        Thr.start()
        logger.debug("Scalping launched")

    def notify(self, observable, event, data={}):
        logger.debug("observer notified")
        mov_log = logging.getLogger('mover')
        obs = observable
        if not isinstance(data, type({})):
            raise ValueError("data need to be a dict")
        if event == 'buy':
            mov_log.info(
                "bought %s with margin of %s " % (obs.product, obs.margin) +
                "with gain of %f and loss of %f" % (
                    data['gain'], data['loss']))
            # ADD HANDLER
            pass
        elif event == 'sell':
            mov_log.info(
                "sold %s with margin of %s with " % (obs.product, obs.margin) +
                "gain of %f and loss of %f" % (data['gain'], data['loss']))
            # ADD HANDLER
            pass
        elif event == 'unlock_run':
            self.run_flag = True

    @abc.abstractmethod
    def update(self):
        """main run faction"""

    @abc.abstractmethod
    def run(self):
        """main run faction"""

    def get_margin(self):
        """get the margin of movement"""
        # free_funds = self.handler.api.get_bottom_info('free_funds')
        free_funds = 10000
        max_margin_risk = self.strategy['max_margin_risk']
        max_trans = self.strategy['max_trans']
        return free_funds * max_margin_risk / max_trans
