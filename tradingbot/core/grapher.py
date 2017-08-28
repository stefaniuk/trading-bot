from threading import Thread
from tradingAPI import API

import time

class Grapher(object):
    def __init__(self, conf):
        self.api = API()
        self.config = conf
        self.monitor = conf.config['MONITOR']
        self.prefs = eval(self.monitor['stocks'])
        self.stocks = []
        self.terminate = False

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

    def stop(self):
        self.terminate = True
        self.api.logout()

    def addPrefs(self):
        self.api.clearPrefs()
        self.api.addPrefs(self.prefs)
        self.config.config['MONITOR']['initiated'] = '1'
        self.config.write()

    def updatePrice(self):
        while self.terminate == False:
            self.api.checkStocks(self.prefs)
            time.sleep(1)

    def candlestickUpdate(self):
        while self.terminate == False:
            time.sleep(60)
            for stock in self.api.stocks:
                if not [x for x in self.stocks if x.name == stock.name]:
                    self.stocks.append(CandlestickStock(stock.name))
                candle = [x for x in self.stocks if x.name == stock.name][0]
                prices = [var[1] for var in stock.vars]
                sent = [var[2] for var in stock.vars][-1]
                candle.addRecord(max(prices), min(prices), prices[0], prices[-1])
                candle.sentiment = sent
                self.api.stocks = []
                # DEL
                # print([x[-1] for x in candle.records][-1])


class CandlestickStock(object):
    def __init__(self, name):
        self.name = name
        self.records = []

    def addRecord(self, openstock, maxstock, minstock, closestock):
        self.records.append([openstock, maxstock, minstock, closestock])