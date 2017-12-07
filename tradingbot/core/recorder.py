# -*- coding: utf-8 -*-

"""
tradingbot.core.recorder
~~~~~~~~~~~~~~

This module provides Recorder object that manipulates
monitor account and update records and datasets.
"""

import time
import threading
from tradingAPI import API
from ..patterns import Observable
from ..glob import Glob
from .stocks import CandlestickStock
# exceptions
import tradingAPI.exceptions

# logging
import logging
logger = logging.getLogger('tradingbot.recorder')


class Recorder(Observable):
    """class to analize stocks in monitor account"""
    def __init__(self):
        super().__init__()
        self.config = Glob().mainConf
        self.monitor = self.config.config['monitor']
        self.api = API()
        # init preferences
        Glob().collection['root']['preferences'].extend(self.monitor['stocks'])
        self.prefs = Glob().collection['root']['preferences']
        # init stocks
        self.stocks = []
        # instantiate in Glob
        Glob().recorder = self
        logger.debug("Recorder initiated")

    def start(self):
        """start the grapher and update threads"""
        logger.debug("starting recorder")
        self.api.launch()
        self.api.login(self.monitor['username'], self.monitor['password'])
        if not int(self.monitor['initiated']):
            self._add_prefs()
        else:
            self.api.preferences = self.prefs
        T1 = threading.Thread(target=self.updatePrice)
        T2 = threading.Thread(target=self.candlestickUpdate)
        T1.deamon = True
        T2.deamon = True
        T1.start()
        logger.debug("Thread #%d launched - updatePrice launched" %
                     threading.active_count())
        T2.start()
        logger.debug("Thread #%d launched - candlestickUpdate launched" %
                     threading.active_count())
        Glob().events['REC_LIVE'].set()

    def _add_prefs(self):
        """func to add prefs"""
        self.api.clearPrefs()
        self.api.addPrefs(self.prefs)
        self.config.config['monitor']['initiated'] = 1
        self.config.save()
        logger.debug("Preferences added")

    def stop(self):
        """stop all threads"""
        Glob().events['REC_LIVE'].clear()
        self.api.logout()

    def updatePrice(self):
        """thread function: update price in stocks"""
        while Glob().events['REC_LIVE'].wait(5):
            start = time.time()
            try:
                self.api.checkStocks()
            except ValueError as e:
                logger.warning(e)
                pass
            left = 1 - (time.time() - start)
            # sleep until one second has elapsed
            if left > 0:
                time.sleep(left)

    def candlestickUpdate(self):
        """thread function: update CandlestickStocks"""
        while Glob().events['REC_LIVE'].wait(5):
            Glob().events['REC_LIVE'].wait_terminate(60)
            count = 0
            for stock in self.api.stocks:
                if not [x for x in self.stocks if x.stock == stock]:
                    self.stocks.append(CandlestickStock(stock))
                candle = [x for x in self.stocks if x.stock == stock][0]
                if not stock.market:
                    logger.debug("market closed for %s" % stock.product)
                    continue
                sell_prices = [float(record[0]) for record in stock.records]
                buy_prices = [float(record[1]) for record in stock.records]
                candle.unit = 1
                candle.add_rec(sell_prices[0], max(sell_prices),
                               min(sell_prices), sell_prices[-1],
                               buy_prices[0], max(buy_prices),
                               min(buy_prices), buy_prices[-1])
                # clear recorder values
                stock.records.clear()
                count += 1
            logger.debug("updated %d candlestick" % count)
            self.notify_observers(event='unlock_run')
