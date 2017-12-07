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

    def convert(self, n):
        if not hasattr(self, 'unit'):
            raise NotImplementedError()
        div = n // self.unit
        # sticks divided in sections
        up_sticks = []
        # temp list
        temp = []
        # if rest of div
        discard = len(self.records) % div
        if discard > 0:
            up_sticks.append(self.records[:discard])
        for stick in self.records[discard:]:
            temp.append(stick)
            if len(temp) == div:
                up_sticks.append(temp)
                temp = []
        refine = []
        # get values
        for coll in up_sticks:
            s_op = coll[0][0][0]
            s_mx = max([x[0][1] for x in coll])
            s_mn = min([x[0][2] for x in coll])
            s_cl = coll[0][0][-1]
            b_op = coll[0][1][0]
            b_mx = max([x[1][1] for x in coll])
            b_mn = min([x[1][2] for x in coll])
            b_cl = coll[0][1][-1]
            refine.append([[s_op, s_mx, s_mn, s_cl], [b_op, b_mx, b_mn, b_cl]])
        return refine

    def get_last_sticks(self, n, unit=None, mode='buy'):
        """get last sticks"""
        # handle errors
        if not isinstance(n, int):
            raise ValueError("n has to be int")
        conv_list = {'buy': 1, 'sell': 0}
        if mode not in conv_list.keys():
            raise ValueError("Mode can only be buy or sell")
        # convert
        if unit is not None and isinstance(unit, int):
            recs = self.convert(unit)
        else:
            recs = self.records
        return [x[conv_list[mode]] for x in recs][-n:]

    def get_last_prices(self, n, value='close', unit=None, mode='buy'):
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
        # convert
        if unit is not None and isinstance(unit, int):
            recs = self.convert(unit)
        else:
            recs = self.records
        if isinstance(value, list):
            indexes = [price_conv.index(ind) for ind in value]
            price_list = [list(itemgetter(*indexes)(x[conv_list[mode]]))
                          for x in recs]
        else:
            price_list = [x[conv_list[mode]][price_conv.index(value)]
                          for x in recs]
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
