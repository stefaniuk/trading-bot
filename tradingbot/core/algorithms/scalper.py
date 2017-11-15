# -*- coding: utf-8 -*-

"""
tradingbot.core.algorithms.scalper
~~~~~~~~~~~~~~

This algo is based on the Scalping technique used in day trading,
 it consists of a large number of trasaction with minimal margin
 exploiting volatility and high-risk trading.
"""

from ...glob import Glob
from ..algorithm import BaseAlgorithm
from ..stocks import PredictStock

# logging
import logging
logger = logging.getLogger('tradingbot.algo.Scalper')


class PredictStockScalper(PredictStock):
    """predict stock for scalping algorithm"""
    def __init__(self, candlestick):
        super().__init__(candlestick)
        self.strategy = Glob().collection['scalping']
        self.overbought = self.strategy['overbought']
        self.oversold = self.strategy['oversold']
        self.momentum = []

    def clear(self):
        """avoid memory overlaod"""
        self.momentum = self.momentum[-2:]

    def _check_mom(self):
        """check if it's possible to evaluate momentum"""
        if not all(isinstance(x, float) for x in self.momentum):
            return False
        elif len(self.momentum) < 2:
            return False
        else:
            return True

    def mom_up(self):
        """check if momentum is up"""
        if not self._check_mom():
            return False
        elif (self.momentum[-2] <= self.oversold < self.momentum[-1] and
                self.momentum[-1] <= self.oversold + 10):
            return True
        else:
            return False

    def mom_down(self):
        """check if momentum is down"""
        if not self._check_mom():
            return False
        elif (self.momentum[-2] >= self.overbought > self.momentum[-1] and
                self.momentum[-1] >= self.overbought - 10):
            return True
        else:
            return False

    def auto_limit(self):
        """define gain or loss limit based on last activity"""
        strat_gain = self.strategy['gain_limit']
        strat_loss = self.strategy['loss_limit']
        conf_limit = self.strategy['auto_limit']
        mx = max(self.candle.get_last_prices(conf_limit, value='high'))
        mn = min(self.candle.get_last_prices(conf_limit, value='low'))
        # get the corrected value of limits
        pip = Glob().handler.get_pip(self.product)
        gain = strat_gain * pip
        loss = strat_loss * pip
        # get max variation
        var = (mx - mn) / 2
        corr_var = var * 0.95
        # get maximum and min limit inserted
        mx_lm = max(gain, loss)
        mn_lm = min(gain, loss)
        # if variation too low
        if mx_lm > corr_var:
            # convert pip in 0.75 of variation
            low_vl = corr_var / mx_lm * mn_lm
            high_vl = corr_var
            if strat_gain > strat_loss:
                gain = high_vl
                loss = low_vl
            else:
                gain = low_vl
                loss = high_vl
        logger.debug("gain: %f - loss: %f" % (gain, loss))
        return gain, loss

    def trigger(self):
        if self.ema_50 > self.ema_100 and self.mom_up():
            gain, loss = self.auto_limit()
            logger.info("It's profitable to buy %s" % self.product)
            # notify observer
            self.notify_observers(
                event='buy', data={'gain': gain, 'loss': loss})
        elif self.ema_50 < self.ema_100 and self.mom_down():
            gain, loss = self.auto_limit()
            logger.info("It's profitable to sell %s" % self.product)
            # notify observer
            self.notify_observers(
                event='sell', data={'gain': gain, 'loss': loss})


class Scalper(BaseAlgorithm):
    """Scalper algorithm class"""
    def __init__(self):
        super().__init__('scalping')
        # init preferences
        Glob().collection['root']['preferences'].extend(self.strategy['prefs'])
        self.gain = self.strategy['gain_limit']
        self.loss = self.strategy['loss_limit']
        logger.debug("Scalper algortihm initiated")

    def update(self):
        """update the predict stocks list"""
        margin = self.get_margin()
        for stock in Glob().recorder.stocks:
            try:
                pred_stock = self.check(
                    stock, PredictStockScalper, ['ema', 'stochastic'])
            except InterruptedError:
                continue
            # calculate
            pred_stock.ema_50 = pred_stock.calculator.ema(50)
            pred_stock.ema_100 = pred_stock.calculator.ema(100)
            # get the last price (use the buy price conventionally)
            price = pred_stock.candle.stock.records[-1][1]
            try:
                momentum = pred_stock.calculator.stochastic_oscillator(5, 3, 3)
            # catch highest price equals to lowest
            except ZeroDivisionError:
                logger.warning("momentum: highest price equal to lowest price")
                momentum = None
            # logger.debug(f"Price: %f" % price)
            # logger.debug(f"EMA 50: %f" % pred_stock.ema_50)
            # logger.debug(f"EMA 100: %f" % pred_stock.ema_100)
            # logger.debug(f"Momentum: %s" % momentum)
            pred_stock.momentum.append(momentum)
            pred_stock.margin = margin
            # clear up
            pred_stock.clear()

    def trigger(self):
        """main trigger function"""
        for x in self.stocks:
            # trigger it with stop_limits
            x.trigger()
