import time
# from numpy import mean

from .color import *
from .grapher import Grapher


class Pivot(object):
    def __init__(self, api, conf, logger):
        self.logger = logger
        self.logger.debug("Pivot algortihm initialized")
        self.api = api
        self.conf = conf
        self.graph = Grapher(self.conf, self.logger)
        self.predict_stocks = []

    def getPivotPoints(self):
        for stock in self.graph.stocks:
            high = max([float(x[1]) for x in stock.records])
            low = min([float(x[2]) for x in stock.records])
            close = [float(x[3]) for x in stock.records][-1]
            if not [x for x in self.predict_stocks if x.name == stock.name]:
                self.predict_stocks.append(predictStock(stock.name))
            predict_stock = [x for x in self.predict_stocks if x.name == stock.name][0]
            predict_stock.pp = (high + low + close) / 3
            predict_stock.s1 = (predict_stock.pp * 2) - high
            predict_stock.s2 = predict_stock.pp - (high - low)
            predict_stock.r1 = (predict_stock.pp * 2) - low
            predict_stock.r2 = predict_stock.pp + (high - low)
            self.logger.info(bold(predict_stock.name) + ': ' +\
                str([round(predict_stock.pp, 3), round(predict_stock.s1, 3), round(predict_stock.r1, 3)]))

    def start(self):
        self.graph.start()
        for y in range(2):
            time.sleep(120)
            self.getPivotPoints()
            # for x in self.predict_stocks:
            #     print(printer.info(bold(x.name) + ': ' + str(x.stack)))

    def stop(self):
        self.graph.stop()

class predictStock(object):
    def __init__(self, name):
        self.name = name
        self.prediction = 0
