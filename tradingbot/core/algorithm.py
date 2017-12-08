# -*- coding: utf-8 -*-

"""
tradingbot.core.algorithm
~~~~~~~~~~~~~~

This module define algorithm's abstract class.
"""
import time
import abc
from threading import Thread, active_count
from ..patterns import Observer
from ..glob import Glob
from .calculator import new_calc

# logging
import logging
logger = logging.getLogger('tradingbot.algorithm')


class BaseAlgorithm(Observer, metaclass=abc.ABCMeta):
    """abstract class for all algorithms"""
    def __init__(self, strat):
        super().__init__()
        # config algo
        self.register_obs(Glob().recorder)
        Glob().init_strategy(strat)
        self.strategy = Glob().collection[strat]
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
        logger.debug("Thread #%d launched - %s launched" % (
            active_count(), self.__class__.__name__))

    def check(self, stock, predStock, funcs):
        """check dependencies"""
        # if market is closed
        if not stock.stock.market:
            raise InterruptedError()
        # if stock not found in registry
        if stock not in [x.candle for x in self.stocks]:
            self.stocks.append(predStock(stock))
        pred_stock = [x for x in self.stocks if x.candle == stock][0]
        # if not initiated calculator
        if not hasattr(pred_stock, 'calculator'):
            pred_stock.calculator = new_calc(funcs)(pred_stock)
        # if not observer
        self.register_obs(pred_stock)
        return pred_stock

    def notify(self, observable, event, data={}):
        """event handler"""
        logger.debug("observer notified")
        obs = observable
        if not isinstance(data, dict):
            raise ValueError("data need to be a dict")
        if event == 'unlock_run':
            self.run_flag = True
        elif event == 'buy' or event == 'sell':
            Glob().handler.add_mov(
                obs.product, event, obs.margin, [data['gain'], data['loss']])

    @abc.abstractmethod
    def update(self):
        """main update faction"""

    @abc.abstractmethod
    def trigger(self):
        """main trigger faction"""

    def run(self, sleep_time=0):
        """main run function, here it is the pivot of the algorithm"""
        sleep_time += self.wait_until_start
        while Glob().events['REC_LIVE'].wait(5):
            self.update()
            self.run_flag = False
            sleep_time -= 1
            # after work period
            if sleep_time < 0:
                self.trigger()
                sleep_time = self.unit - 1
            # wait until next update
            while not self.run_flag:
                Glob().events['REC_LIVE'].wait_terminate(1)

    def get_margin(self):
        """get the margin of movement"""
        free_funds = Glob().handler.get_free_funds()
        max_margin_risk = self.strategy['max_margin_risk']
        max_trans = self.strategy['max_trans']
        return free_funds * max_margin_risk / max_trans
