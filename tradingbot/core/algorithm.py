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
        self.stock = [x for x in Glob().recorder.stocks
                      if x.product == self.product][0]
        self.emas = []

    def _clear(self):
        """avoid memory overload"""
        self.emas = self.emas[:50]

    def sma(self, periods, unit=1):
        """calculate the Simple Moving Average"""
        periods *= unit
        records = self.stock.records
        close_list = [x[1][-1] for x in records[-periods:]]
        return sum(close_list) / len(close_list)

    def ema(self, periods, unit=1):
        """calculate the Exponential Moving Average"""
        records = self.stock.records
        close = records[-1][1][-1]
        multiplier = 2 / (periods + 1)
        if len(self.emas) == 0:
            latest_ema = close
        else:
            latest_ema = self.emas[-1]
        ema = (close - latest_ema) * multiplier + latest_ema
        self.emas.append(ema)
        # clear up
        self._clear()
        return ema

    def stochastic_oscillator_5_3_3(self, k_fast_list, k_list):
        """calculate the Stochastic Oscillator 5 3 3"""
        records = self.stock.records[-5:]
        close = records[-1][1][-1]
        highest_high = max([x[1][1] for x in records])
        lowest_low = min([x[1][2] for x in records])
        k_fast = (close - lowest_low) / (highest_high - lowest_low) * 100
        k_fast_list.append(k_fast)
        k = sum(k_fast_list[-3:]) / 3
        k_list.append(k)
        d = sum(k_list[-3:]) / 3
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
        T3 = Thread(target=Glob().recorder.start)
        T4 = Thread(target=Glob().handler.start)
        T5 = Thread(target=self.run, args=(sleep_time,))
        T5.deamon = True
        T3.start()
        T4.start()
        T3.join()
        time.sleep(65)
        T4.join()
        T5.start()
        logger.debug("Scalping thread #5 launched")

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
