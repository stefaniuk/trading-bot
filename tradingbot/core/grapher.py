# -*- coding: utf-8 -*-

"""
tradingbot.core.grapher
~~~~~~~~~~~~~~

This module provides grapher object that manipulates
monitor account and update records and datasets.
"""

import time
import threading
from tradingAPI import API
from tradingbot.core import events
from .color import *
from .logger import logger
from .utils import _close_to
from .stocks import CandlestickStock


class Grapher(object):
    """class to analize stocks in monitor account"""
    def __init__(self, conf, strat):
        self.config = conf
        self.strategy = strat
        self.monitor = conf.config['monitor']
        self.api = API(conf.config['logger_level_api'])
        self.prefs = self.monitor['stocks']
        self.prefs.extend(strat['prefs'])
        self.stocks = []
        self.count = 0
        logger.debug("Grapher initialized")

    def start(self):
        """start the grapher and update threads"""
        self.api.launch()
        if not self.api.login(self.monitor['username'],
                              self.monitor['password']):
            logger.critical("grapher failed to start")
            self.stop()
        if not int(self.monitor['initiated']):
            self.addPrefs()
        T1 = threading.Thread(target=self.updatePrice)
        T2 = threading.Thread(target=self.candlestickUpdate)
        T1.deamon = True
        T2.deamon = True
        T1.start()
        T2.start()
        events.LIVE.set()
        logger.debug("Price updater thread #1 launched")
        logger.debug("Candlestick updater thread #2 launched")

    def stop(self):
        """stop all threads"""
        events.LIVE.clear()
        try:
            self.api.logout()
        except tradingAPI.exceptions.BrowserException as e:
            logger.warning(f"Warning: {e}")

    def addPrefs(self):
        """func to add prefs"""
        try:
            self.api.clearPrefs()
            self.api.addPrefs(self.prefs)
            self.config.config['monitor']['initiated'] = 1
            self.config.save()
            logger.debug("Preferencies added")
        except Exception:
            logger.error("Failed to add prefs")
            raise

    def updatePrice(self):
        """thread function: update price in stocks"""
        while events.LIVE.wait(5):
            self.api.checkStocks(self.prefs)
            time.sleep(1)

    def candlestickUpdate(self):
        """thread function: update CandlestickStocks"""
        while events.LIVE.wait(5):
            events.LIVE.wait_terminate(60)
            count = 0
            for stock in self.api.stocks:
                if stock.market:
                    if not [x for x in self.stocks if x.name == stock.name]:
                        self.stocks.append(CandlestickStock(stock.name))
                    candle = [x for x in self.stocks
                              if x.name == stock.name][0]
                    prices = [float(var[0]) for var in stock.vars]
                    sent = [var[1] for var in stock.vars][-1]
                    candle.addRecord(prices[0], max(prices), min(prices),
                                     prices[-1])
                    candle.sentiment = sent
                    count += 1
                else:
                    if [x for x in self.stocks if x.name == stock.name]:
                        self.stocks.remove([x for x in self.stocks
                                            if x.name == stock.name][0])
            self.count += 1
            logger.debug(f"updated {count} candlestick")

    def isDoji(self, name):
        """check if there is a doji"""
        stock = [x for x in self.stocks if x.name == name][0]
        op = stock.records[-1][0]
        cl = stock.records[-1][-1]
        if op == cl:
            logger.debug(f"doji on {bold(name)}")
            return True
        else:
            return False

    def isClose(self, name, value):
        """check if the value is close to the newest price of name"""
        price = float(
            [x.vars[-1] for x in self.api.stocks if x.name == name][0][0])
        records = [x.records for x in self.stocks if x.name == name][0]
        mx = max([float(x[1]) for x in records])
        mn = min([float(x[2]) for x in records])
        swap = self.strategy['swap'] * (mx - mn)
        logger.debug(f"swap: {swap}")
        if _close_to(price, value, swap):
            logger.debug(f"{price} is close to {value}")
            return True
