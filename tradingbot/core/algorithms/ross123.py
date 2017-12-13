# -*- coding: utf-8 -*-

"""
tradingbot.core.algorithms.ross123
~~~~~~~~~~~~~~

This algo is based on Joe Ross techniques used in day trading,
 there are 123 high and low.
"""
import time
from ...glob import Glob
from ..algorithm import BaseAlgorithm, check_secondary
from ..stocks import PredictStock

# logging
import logging
logger = logging.getLogger('tradingbot.algo.Ross123')


class PredictStockRoss123(PredictStock):
    """predict stock for ross123 algorithm"""
    def __init__(self, candlestick):
        super().__init__(candlestick)
        self.strategy = Glob().collection['ross123']
        self.unit = self.strategy['unit']
        self.secondary = check_secondary(
            self.strategy['secondary-prefs'], self.product)

    def auto_limit(self):
        """define gain or loss limit based on last activity"""
        conf_limit = self.strategy['auto_limit']
        mx_var = self.strategy['max_variation']
        mx_loss = self.strategy['max_loss']
        mx = max(self.candle.get_last_prices(conf_limit, 'high', self.unit))
        mn = min(self.candle.get_last_prices(conf_limit, 'low', self.unit))
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
        self.notify_observers(event=mode, data={'gain': gain, 'loss': loss,
                              'secondary': self.secondary})


class Ross123(BaseAlgorithm):
    def __init__(self):
        super().__init__('ross123')
        self.unit = self.strategy['unit']
        self.wait_until_start = self.strategy['wait_start']
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
            logger.debug("aborted")

    class Base123(object):
        """high and low object observable"""
        def __init__(self, pred_stock, unit):
            self.stock = pred_stock
            self.candle = pred_stock.candle
            self.unit = unit
            # trigger 1 2 3 default
            self.trigger = Ross123.BooList(5)

        def check_last(self, part, truncate=True, n=4):
            """check last records with part in it"""
            last_stocks = self.candle.get_last_sticks(n, self.unit)
            if part in last_stocks:
                # restrict list
                ind = last_stocks.index(part)
                # if truncate
                if truncate:
                    ind += 1
                if not last_stocks[ind:]:
                    logger.warning("BUG #NAPOLEON")
                    return
                return last_stocks[ind:]
            else:
                # aborting
                self.trigger.clear()
                return

        def check(self):
            """facade function"""
            if not self.candle.stock.market:
                return
            if not self.trigger[0]:
                self.check_first()
            elif not self.trigger[1]:
                self.check_second()
            elif not self.trigger[2]:
                self.check_third()
            elif not self.trigger[3]:
                self.check_third_supp()
            elif not self.trigger[4]:
                self.check_third_exploit()

    class High123(Base123):
        """High123 conformation"""
        def __init__(self, pred_stock, unit):
            super().__init__(pred_stock, unit)

        def check_first(self):
            """check if last high is lower than previus"""
            # *~ trigger 1 ~*
            # clear trigger
            self.trigger_1 = None
            last_high = self.candle.get_last_prices(2, 'high', self.unit)
            if last_high[0] > last_high[1]:
                self.trigger.set(0)
                # set trigger with last candlestick
                self.trigger_1 = self.candle.get_last_sticks(1, self.unit)[0]

        def check_second(self):
            """check if last low is lower than previous"""
            # *~ trigger 2 ~*
            # clear trigger
            self.trigger_2 = None
            last_stocks = self.check_last(self.trigger_1, False)
            if last_stocks is None:
                return
            if last_stocks[-1][2] > last_stocks[-2][2]:
                self.trigger.set(1)
                # set trigger with last candlestick
                self.trigger_2 = self.candle.get_last_sticks(1, self.unit)[0]

        def check_third(self):
            """check third condition"""
            # *~ trigger 3 ~*
            self.trigger_3 = None
            last_stocks = self.check_last(self.trigger_2)
            if last_stocks is None:
                return
            mn = min(x[2] for x in last_stocks)
            mx = max(x[1] for x in last_stocks)
            if mn > self.trigger_2[2] and mx > self.trigger_2[1]:
                self.trigger.set(2)
                # set trigger with last candlestick
                self.trigger_3 = self.candle.get_last_sticks(1, self.unit)[0]

        def check_third_supp(self):
            # *~ trigger 3.1 ~*
            last_stocks = self.check_last(self.trigger_3)
            if last_stocks is None:
                return
            mn = min(x[2] for x in last_stocks)
            mx = max(x[1] for x in last_stocks)
            if mn < self.trigger_2[2] and mx < self.trigger_2[1]:
                self.trigger.set(3)

        def check_third_exploit(self):
            """check how to exploit the trend"""
            # *~ trigger 3.2 ~*
            last_stocks = self.check_last(self.trigger_3)
            if last_stocks is None:
                return
            if last_stocks[-1][3] < self.trigger_2[1]:
                self.trigger.set(4)

    class Low123(Base123):
        """Low123 conformation"""
        def __init__(self, pred_stock, unit):
            super().__init__(pred_stock, unit)

        def check_first(self):
            """check if last low is higher than previus"""
            # *~ trigger 1 ~*
            self.trigger_1 = None
            last_low = self.candle.get_last_prices(2, 'low', self.unit)
            if last_low[0] < last_low[1]:
                self.trigger.set(0)
                # set trigger with last candlestick
                self.trigger_1 = self.candle.get_last_sticks(1, self.unit)[0]

        def check_second(self):
            """check if last high is higher than previous"""
            # *~ trigger 2 ~*
            # clear trigger
            self.trigger_2 = None
            last_stocks = self.check_last(self.trigger_1, False)
            if last_stocks is None:
                return
            if last_stocks[-1][1] > last_stocks[-2][1]:
                self.trigger.set(1)
                # set trigger with last candlestick
                self.trigger_2 = self.candle.get_last_sticks(1, self.unit)[0]

        def check_third(self):
            """check third condition"""
            # *~ trigger 3 ~*
            self.trigger_3 = None
            last_stocks = self.check_last(self.trigger_2)
            if last_stocks is None:
                return
            mn = min(x[2] for x in last_stocks)
            mx = max(x[1] for x in last_stocks)
            if mn < self.trigger_2[2] and mx < self.trigger_2[1]:
                self.trigger.set(2)
                # set trigger with last candlestick
                self.trigger_3 = self.candle.get_last_sticks(1, self.unit)[0]

        def check_third_supp(self):
            # *~ trigger 3.1 ~*
            last_stocks = self.check_last(self.trigger_3)
            if last_stocks is None:
                return
            mn = min(x[2] for x in last_stocks)
            mx = max(x[1] for x in last_stocks)
            if mn > self.trigger_2[2] and mx > self.trigger_2[1]:
                self.trigger.set(3)

        def check_third_exploit(self):
            """check how to exploit the trend"""
            # *~ trigger 3.2 ~*
            last_stocks = self.check_last(self.trigger_3)
            if last_stocks is None:
                return
            if last_stocks[-1][3] > self.trigger_2[2]:
                self.trigger.set(4)

    def update(self):
        """update the predict stocks list"""
        marg = self.get_margin()
        for stock in Glob().recorder.stocks:
            try:
                pred_stock = self.check(stock, PredictStockRoss123, ['ema'])
            except InterruptedError:
                continue
            # calculate
            pred_stock.sma_30 = pred_stock.calculator.ema(10)
            pred_stock.sma_60 = pred_stock.calculator.ema(30)
            pred_stock.margin = marg

    def trigger(self):
        for x in self.stocks:
            if not hasattr(x, 'High'):
                x.High = Ross123.High123(x, self.unit)
            if not hasattr(x, 'Low'):
                x.Low = Ross123.Low123(x, self.unit)
            # check conditions
            # simple moving price average
            if x.sma_30 > x.sma_60:
                x.High.check()
            elif x.sma_30 < x.sma_60:
                x.Low.check()
            if False not in x.High.trigger:
                logger.debug("all conditions met for %s" % x.product)
                x.trigger('sell')
                x.High.trigger.clear()
            elif False not in x.Low.trigger:
                logger.debug("all conditions met for %s" % x.product)
                x.trigger('buy')
                x.Low.trigger.clear()
