from tradingAPI import API
import asyncio

class Grapher(object):
    def __init__(self, conf):
        self.config = conf
        self.monitor = conf.config['MONITOR']
        self.prefs = eval(self.monitor['stocks'])
        self.stocks = []

    def start(self):
        self.api = API()
        self.api.login(self.monitor['username'], self.monitor['password'])
        if not self.monitor['initiated']:
            self.addPrefs()

    def addPrefs(self):
        self.clearPrefs()
        self.addPrefs(self.prefs)
        self.config.config['MONITOR']['initiated'] = 1
        self.config.write()

    async def updatePrice(self):
        while True:
            self.api.checkStocks(self.prefs)
            await asyncio.sleep(1)

    async def candlestickUpdate(self):
        while True:
            await asyncio.sleep(60)
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
                print([x[-1] for x in candle.records][-1])


class CandlestickStock(object):
    def __init__(self, name):
        self.name = name
        self.records = []

    def addRecord(self, openstock, maxstock, minstock, closestock):
        self.records.append([openstock, maxstock, minstock, closestock])