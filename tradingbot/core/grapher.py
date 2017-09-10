import time
from threading import Thread, Event
import tradingAPI.exceptions
from tradingAPI import API
from .stocks import CandlestickStock
from .logger import *
from .color import *


class Grapher(object):
    def __init__(self, conf):
        logger.debug("Grapher initialized")
        self.config = conf
        self.monitor = conf.config['monitor']
        self.api = API(self.config.config['logger_level'])
        self.prefs = self.monitor['stocks']
        self.stocks = []
        self.live = Event()

    def _waitTerminate(self, interval):
        for x in range(interval):
            if self.live.is_set():
                time.sleep(1)
            else:
                return False

    def _closeTo(self, val1, val2, swap=0.05):
        swap2 = val2 * swap
        if val2 - swap2 < val1 and val1 < val2 + swap2:
            return True
        else:
            return False

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
        T2.start()
        self.live.set()
        logger.debug("Price updater thread #1 launched")
        logger.debug("Candlestick updater thread #2 launched")

    def stop(self):
        self.live.clear()
        try:
            self.api.logout()
        except tradingAPI.exceptions.BrowserException as e:
            logger.warning(f"Warning: {e}")

    def addPrefs(self):
        self.api.clearPrefs()
        self.api.addPrefs(self.prefs)
        self.config.config['monitor']['initiated'] = 1
        self.config.save()
        logger.debug('Preferencies added')

    def updatePrice(self):
        while self.live.wait(10):
            self.api.checkStocks(self.prefs)
            time.sleep(1)

    def candlestickUpdate(self):
        while self.live.wait(10):
            tm = self._waitTerminate(60)
            if tm is not False:
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
                    else:
                        if [x for x in self.stocks if x.name == stock.name]:
                            self.stocks.remove([x for x in self.stocks if x.name == stock.name][0])
                logger.debug(f"updated {count} candlestick")

    def isDoji(self, name):
        stock = [x for x in self.stocks if x.name == name][0]
        op = stock.records[-1][0]
        cl = stock.records[-1][-1]
        if op == cl:
            logger.debug(f"doji on {bold(name)}")
            return True
        else:
            return False

    def isClose(self, name, value):
        price = float([x.vars[-1] for x in self.api.stocks if x.name == name][0][0])
        swap = float(self.config.config['strategy']['swap'])
        if self._closeTo(price, value, swap):
            logger.debug(f"{price} is close to {value}")
            return True
