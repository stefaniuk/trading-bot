# -*- coding: utf-8 -*-

"""
tradingbot.core.stocks
~~~~~~~~~~~~~~

This module provides stocks objects.
"""


class BaseStock(object):
    def __init__(self, name):
        self.name = name
        self.records = []

    def _clear(self, value):
        self.records = self.records[-value:]


class CandlestickStock(BaseStock):
    def __init__(self, name):
        super().__init__(name)
        self.sentiment = None

    def addRecord(self, openstock, maxstock, minstock, closestock):
        self.records.append([openstock, maxstock, minstock, closestock])
        self._clear(250)


class PredictStock(BaseStock):
    def __init__(self, candlestick):
        super().__init__(candlestick.name)
        self.candlestick = candlestick
        self.prediction = 0

    # DEPRECATED
    # def add(self, val):
    #     self.prediction += (val * (1 - self.prediction))
    #
    # def multiply(self, val):
    #     self.prediction *= val
    #     if self.prediction > 1:
    #         self.prediction = 1


class PredictStockScalping(PredictStock):
    def __init__(self, candlestick):
        super().__init__(candlestick)
        self.momentum = []
        self.k_fast_list = []
        self.k_list = []

    def clear(self):
        self.momentum = self.momentum[-2:]
        self.k_fast_list = self.k_fast_list[-3:]
        self.k_list = self.k_list[-3:]

    def _check_mom(self):
        if not isinstance(self.momentum, type(0.0)):
            return False
        elif len(self.momentum) < 2:
            return False
        else:
            return True

    def mom_up(self):
        self._check_mom()
        if self.momentum[-2] <= 20 < self.momentum[-1]:
            return True
        else:
            return False

    def mom_down(self):
        self._check_mom()
        if self.momentum[-2] >= 80 > self.momentum[-1]:
            return True
        else:
            return False


class StockAnalysis(object):
    def __init__(self, name):
        self.name = name
        self.volatility = None
