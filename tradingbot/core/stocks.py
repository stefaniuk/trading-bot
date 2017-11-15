# -*- coding: utf-8 -*-

"""
tradingbot.core.stocks
~~~~~~~~~~~~~~

This module provides stocks objects.
"""

import abc
from operator import itemgetter
from ..patterns import Observable


class BaseStock(object):
    """abstract class for stock"""
    def __init__(self, product):
        self.product = product
        self.records = []

    def clear(self, value):
        """to avoid memory overload"""
        self.records = self.records[-value:]


class CandlestickStock(BaseStock):
    """stock for data storing"""
    def __init__(self, stock):
        super().__init__(stock.product)
        self.stock = stock
        # self.sentiment = None

    def add_rec(self, sl_op, sl_mx, sl_mn, sl_cl, by_op, by_mx, by_mn, by_cl):
        """add value to records"""
        self.records.append(
            [[sl_op, sl_mx, sl_mn, sl_cl], [by_op, by_mx, by_mn, by_cl]])
        self.clear(250)

    def get_last_prices(self, n, mode='buy', value='close'):
        """get the latest prices"""
        # handle errors
        if not isinstance(n, int):
            raise ValueError("n has to be int")
        conv_list = {'buy': 1, 'sell': 0}
        if mode not in conv_list.keys():
            raise ValueError("Mode can only be buy or sell")
        price_conv = ['open', 'high', 'low', 'close']
        if value not in price_conv and not isinstance(value, list):
            raise ValueError("Mode can only be open, high, low or close")
        if isinstance(value, list):
            indexes = [price_conv.index(ind) for ind in value]
            price_list = [list(itemgetter(*indexes)(x[conv_list[mode]]))
                          for x in self.records]
        else:
            price_list = [x[conv_list[mode]][price_conv.index(value)]
                          for x in self.records]
        return price_list[-n:]


class PredictStock(BaseStock, Observable, metaclass=abc.ABCMeta):
    """abstract for predict stock"""
    def __init__(self, candlestick):
        BaseStock.__init__(self, candlestick.product)
        Observable.__init__(self)
        self.candle = candlestick

    @abc.abstractmethod
    def trigger(self):
        """trigger the observer if actioned by conditions"""


# class StockAnalysis(object):
#     def __init__(self, product):
#         self.product = product
#         self.volatility = None
