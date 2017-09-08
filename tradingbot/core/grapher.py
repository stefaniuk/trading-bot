import time
from threading import Thread
import tradingAPI.exceptions
from tradingAPI import API
from .color import *
from .logger import *


class Grapher(object):
    def __init__(self, conf):
        logger.debug("Grapher initialized")
        self.config = conf
        self.monitor = conf.config['monitor']
        self.api = API(self.config.config['logger_level'])
        self.prefs = self.monitor['stocks']
        self.stocks = []
        self.terminate = False

    def _waitTerminate(self, interval):
        for x in range(interval):
            if self.terminate is False:
                time.sleep(1)
            else:
                return 0

    def _closeTo(self, val1, val2, swap=0.05):
        swap2 = val2 * swap
        if val2 - swap2 < val1 and val1 < val2 + swap2:
            return 1
        else:
            return 0

    def start(self):
        self.api.launch()
        self.api.login(self.monitor['username'], self.monitor['password'])
        if not int(self.monitor['initiated']):
            self.addPrefs()
        T1 = Thread(target=self.updatePrice)
        T2 = Thread(target=self.candlestickUpdate)
        T1.deamon = True
        T2.deamon = True
        T1.start()
        logger.debug("Price updater thread #1 launched")
        T2.start()
        logger.debug("Candlestick updater thread #2 launched")

    def stop(self):
        self.terminate = True
        try:
            self.api.logout()
        except tradingAPI.exceptions.BrowserException as e:
            logger.warning(f"Warning: {e}")

    def addPrefs(self):
        self.api.clearPrefs()
        time.sleep(2)
        self.api.addPrefs(self.prefs)
        self.config.config['initiated'] = '1'
        self.config.save()
        logger.debug('Preferencies added')

    def updatePrice(self):
        while self.terminate is False:
            self.api.checkStocks(self.prefs)
            time.sleep(1)

    def candlestickUpdate(self):
        while self.terminate is False:
            tm = self._waitTerminate(60)
            if tm != 0:
                count = 0
                for stock in self.api.stocks:
                    if stock.market:
                        if not [x for x in self.stocks if x.name == stock.name]:
                            self.stocks.append(CandlestickStock(stock.name))
                        candle = [x for x in self.stocks if x.name == stock.name][0]
                        prices = [var[0] for var in stock.vars]
                        sent = [var[1] for var in stock.vars][-1]
                        candle.addRecord(max(prices), min(prices), prices[0],
                                         prices[-1])
                        candle.sentiment = sent
                        count += 1
                logger.debug(f"updated {count} candlestick")

    def isDoji(self, name):
        stock = [x for x in self.stocks if x.name == name][0]
        op = stock.records[-1][0]
        cl = stock.records[-1][-1]
        if op == cl:
            logger.debug("doji on {bold(name)}")
            return 1
        else:
            return 0

    def isClose(self, name, value):
        price = float([x.vars[-1] for x in self.api.stocks if x.name == name][0][0])
        swap = float(self.config.config['strategy']['swap'])
        if self._closeTo(price, value, swap):
            logger.debug("{price} is close to {value}")
            return 1


class CandlestickStock(object):
    def __init__(self, name):
        self.name = name
        self.records = []

    def addRecord(self, openstock, maxstock, minstock, closestock):
        self.records.append([openstock, maxstock, minstock, closestock])
