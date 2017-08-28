import asyncio
from numpy import mean

from .grapher import Grapher


import time


class Pivot(object):
    def __init__(self, api, conf):
        self.api = api
        self.conf = conf
        self.graph = Grapher(self.conf)
        self.predict_stocks = []

    def getPivotPoints(self):
        for stock in self.graph.stocks:
            high = mean([float(x[1]) for x in stock.records])
            low = mean([float(x[2]) for x in stock.records])
            close = mean([float(x[3]) for x in stock.records])
            if not [x for x in self.predict_stocks if x.name == stock.name]:
                self.predict_stocks.append(predictStock(stock.name))
            predict_stock = [x for x in self.predict_stocks if x.name == stock.name][0]
            predict_stock.pp = (high + low + close) / 3
            predict_stock.s1 = (predict_stock.pp * 2) - high
            predict_stock.s2 = predict_stock.pp - (high - low)
            predict_stock.r1 = (predict_stock.pp * 2) - low
            predict_stock.r2 = predict_stock.pp + (high - low)
            predict_stock.stack = [predict_stock.pp, predict_stock.s1, predict_stock.r1]

    def start(self):
        self.graph.start()
        for y in range(1):
            time.sleep(70)
            self.getPivotPoints()
            print([x.stack for x in self.predict_stocks if x.name == 'bitcoin'])

    def stop(self):
        self.graph.stop()

class predictStock(object):
    def __init__(self, name):
        self.name = name
        self.prediction = 0
