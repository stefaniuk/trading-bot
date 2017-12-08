# -*- coding: utf-8 -*-

"""
tradingbot.core.calculator
~~~~~~~~~~~~~~

This module define algorithm's calculator, complex predictive functions
(buy conventionally)
"""

# logging
import logging
logger = logging.getLogger('tradingbot.core.calculator')


def new_calc(funcs):
    """factory method"""
    class BaseCalculator(object):
        """base calculator abstract class"""
        def __init__(self, p_stock):
            self.product = p_stock.product
            self.stock = p_stock.candle
    acceptable = ['ema', 'sma', 'stochastic']
    # check if acceptable
    for x in funcs:
        if x not in acceptable:
            raise ValueError("%s not acceptable" % x)
    Calc = BaseCalculator
    for x in funcs:
        # for exponential moving average
        if x == 'ema':
            Calc.ema = ema_tool()
            Calc.emas = {}
            Calc.k_fast_list = []
            Calc.k_list = []
        # for simple moving average
        elif x == 'sma':
            Calc.sma = sma_tool()
        # for stochastic oscillator
        elif x == 'stochastic':
            Calc.stochastic_oscillator = stochastic_tool()
    return Calc


def ema_tool():
    """build ema function"""
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
        for key in self.emas.keys():
            self.emas[key] = self.emas[key][-50:]
        return ema
    return ema


def sma_tool():
    """build sma function"""
    def sma(self, periods):
        """calculate the Simple Moving Average"""
        close_list = [x[1][-1] for x in self.stock.records[-periods:]]
        return sum(close_list) / len(close_list)
    return sma


def stochastic_tool():
    """build stochastic_oscillator function"""
    def stochastic_oscillator(self, k_period, k_slow_period, d_period):
        """calculate the Stochastic Oscillator 5 3 3"""
        records = self.stock.records[-k_period:]
        close = records[-1][1][-1]
        highest_high = max([x[1][1] for x in records])
        lowest_low = min([x[1][2] for x in records])
        k_fast = (close - lowest_low) / (highest_high - lowest_low) * 100
        self.k_fast_list.append(k_fast)
        del self.k_fast_list[:-k_slow_period]
        k = sum(self.k_fast_list) / len(self.k_fast_list)
        self.k_list.append(k)
        del self.k_list[:-d_period]
        d = sum(self.k_list) / len(self.k_list)
        return d
    return stochastic_oscillator
