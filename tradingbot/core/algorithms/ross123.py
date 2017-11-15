# -*- coding: utf-8 -*-

"""
tradingbot.core.algorithms.ross123
~~~~~~~~~~~~~~

This algo is based on Joe Ross techniques used in day trading,
 there are 123 high and low.
"""

from ...glob import Glob
from ..algorithm import BaseAlgorithm
from ..stocks import PredictStock

# logging
import logging
logger = logging.getLogger('tradingbot.algo.Ross123')


class PredictStockRoss123(PredictStock):
    """predict stock for ross123 algorithm"""
    def __init__(self, candlestick):
        super().__init__(candlestick)
        self.strategy = Glob().collection['ross123']

    def auto_limit(self):
        """define gain or loss limit based on last activity"""
        conf_limit = self.strategy['auto_limit']
        mx_var = self.strategy['max_variation']
        mx_loss = self.strategy['max_loss']
        mx = max(self.candle.get_last_prices(conf_limit, value='high'))
        mn = min(self.candle.get_last_prices(conf_limit, value='low'))
        # get the variation
        var = (mx - mn) * mx_var
        gain = var
        loss = var * mx_loss
        logger.debug("gain: %f - loss: %f" % (gain, loss))
        return gain, loss

    def trigger(self, mode):
        """trigger buy or sell"""
        logger.info("it's profitable to %s %s" % (mode, self.product))
        gain, loss = self.auto_limit()
        self.notify_observers(event=mode, data={'gain': gain, 'loss': loss})


class Ross123(BaseAlgorithm):
    def __init__(self):
        super().__init__('ross123')
        self.strategy = Glob().collection['ross123']
        logger.debug("Ross123 algorithm initiated")

    class BooList(list):
        """list of boolean values"""
        def __init__(self, n):
            super().__init__([False for _ in range(n)])

        def set(self, n):
            """make True a val"""
            if n >= self.__len__():
                raise IndexError("max n is %d" % self.__len__())
            self.__setitem__(n, True)
            logger.debug("condition %d met" % n)

        def clear(self):
            """all vals False"""
            for x in range(self.__len__()):
                self.__setitem__(x, False)
            logger.debug("aborted" % n)

    class Base123(object):
        """high and low object observable"""
        def __init__(self, pred_stock):
            self.stock = pred_stock
            self.candle = pred_stock.candle
            # trigger 1 2 3 default
            self.trigger = Ross123.BooList(4)

        def check(self):
            """facade function"""
            logger.debug("checking %d for %s" % (
                self.trigger.index(False), self.stock.product))
            if not self.trigger[0]:
                self.check_first()
            elif not self.trigger[1]:
                self.check_second()
            elif not self.trigger[2]:
                self.check_third()
            elif not self.trigger[3]:
                self.check_third_supp()

    class High123(Base123):
        """High123 conformation"""
        def __init__(self, pred_stock):
            super().__init__(pred_stock)

        def check_first(self):
            """check if last high is lower than previus"""
            # *~ trigger 1 ~*
            last_high = self.candle.get_last_prices(2, value='high')
            if last_high[0] > last_high[1]:
                logger.debug("checking first for high")
                self.trigger.set(0)

        def check_second(self):
            """check if last low is lower than previous"""
            # *~ trigger 2 ~*
            # clear trigger
            self.trigger_2 = None
            last_low = self.candle.get_last_prices(2, value='low')
            if last_low[0] < last_low[1]:
                self.trigger.set(1)
                # set trigger with last candlestick
                self.trigger_2 = self.candle.records[1][-1]

        def check_third(self):
            """check third condition"""
            # *~ trigger 3 ~*
            self.trigger_3 = None
            last_stocks = self.candle.records[1][-4:]
            if self.trigger_2 in last_stocks:
                # restrict list
                last_stocks = last_stocks[
                    last_stocks.index(self.trigger_2) + 1:]
            else:
                # aborting
                self.trigger.clear()
            mn = min(x for x in last_stocks[1])
            mx = max(x for x in last_stocks[2])
            if mn > self.trigger_2[1] and mx > self.trigger_2[2]:
                self.trigger.set(2)
                # set trigger with last candlestick
                self.trigger_3 = self.candle.records[1][-1]

        def check_third_supp(self):
            # *~ trigger 3.1 ~*
            last_stocks = self.candle.records[1][-4:]
            if self.trigger_2 in last_stocks:
                # restrict list
                last_stocks = last_stocks[
                    last_stocks.index(self.trigger_3) + 1:]
            else:
                # aborting
                self.trigger.clear()
            mn = min(x for x in last_stocks[1])
            mx = max(x for x in last_stocks[2])
            if mn < self.trigger_2[1] and mx < self.trigger_2[2]:
                self.trigger.set(4)

    class Low123(Base123):
        """Low123 conformation"""
        def __init__(self, pred_stock):
            super().__init__(pred_stock)

        def check_first(self):
            """check if last low is higher than previus"""
            # *~ trigger 1 ~*
            last_low = self.candle.get_last_prices(2, value='low')
            if last_low[0] < last_low[1]:
                logger.debug("checking first for low")
                self.trigger.set(0)

        def check_second(self):
            """check if last high is higher than previous"""
            # *~ trigger 2 ~*
            # clear trigger
            self.trigger_2 = None
            last_high = self.candle.get_last_prices(2, value='high')
            if last_high[0] < last_high[1]:
                self.trigger.set(1)
                # set trigger with last candlestick
                self.trigger_2 = self.candle.records[1][-1]

        def check_third(self):
            """check third condition"""
            # *~ trigger 3 ~*
            self.trigger_3 = None
            last_stocks = self.candle.records[1][-4:]
            if self.trigger_2 in last_stocks:
                # restrict list
                last_stocks = last_stocks[
                    last_stocks.index(self.trigger_2) + 1:]
            else:
                # aborting
                self.trigger.clear()
            mn = min(x for x in last_stocks[1])
            mx = max(x for x in last_stocks[2])
            if mn < self.trigger_2[1] and mx < self.trigger_2[2]:
                self.trigger.set(2)
                # set trigger with last candlestick
                self.trigger_3 = self.candle.records[1][-1]

        def check_third_supp(self):
            # *~ trigger 3.1 ~*
            last_stocks = self.candle.records[1][-4:]
            if self.trigger_2 in last_stocks:
                # restrict list
                last_stocks = last_stocks[
                    last_stocks.index(self.trigger_3) + 1:]
            else:
                # aborting
                self.trigger.clear()
            mn = min(x for x in last_stocks[1])
            mx = max(x for x in last_stocks[2])
            if mn > self.trigger_2[1] and mx > self.trigger_2[2]:
                self.trigger.set(3)

    def update(self):
        """update the predict stocks list"""
        for stock in Glob().recorder.stocks:
            try:
                pred_stock = self.check(stock, PredictStockRoss123, ['ema'])
            except InterruptedError:
                continue
            # calculate
            pred_stock.sma_30 = pred_stock.calculator.ema(10)
            pred_stock.sma_60 = pred_stock.calculator.ema(30)
            pred_stock.margin = self.get_margin()

    def trigger(self):
        for x in self.stocks:
            if not hasattr(x, 'High'):
                x.High = Ross123.High123(x)
            if not hasattr(x, 'Low'):
                x.Low = Ross123.Low123(x)
            # check conditions
            # simple moving price average
            if x.sma_30 > x.sma_60:
                x.High.check()
            elif x.sma_30 < x.sma_60:
                x.Low.check()
            if (False not in x.High.trigger and x.candle.get_last_prices(
                    1, value='close') < x.High.trigger_2[2]):
                logger.debug("all conditions met for %s" % x.product)
                x.trigger('sell')
                x.High.trigger.clear()
            elif (False not in x.Low.trigger and x.candle.get_last_prices(
                    1, value='close') > x.Low.trigger_2[1]):
                logger.debug("all conditions met for %s" % x.product)
                x.trigger('buy')
                x.Low.trigger.clear()
