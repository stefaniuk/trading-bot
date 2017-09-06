import time
from .color import *
from .logger import *
from .grapher import Grapher


class Pivot(object):
    def __init__(self, conf):
        logger.debug("Pivot algortihm initialized")
        self.conf = conf
        self.graph = Grapher(self.conf)
        self.predict_stocks = []

    def getPivotPoints(self):
        for stock in self.graph.stocks:
            high = max([float(x[1]) for x in stock.records])
            low = min([float(x[2]) for x in stock.records])
            close = [float(x[3]) for x in stock.records][-1]
            if not [x for x in self.predict_stocks if x.name == stock.name]:
                self.predict_stocks.append(predictStock(stock.name))
            predict_stock = [
                x for x in self.predict_stocks if x.name == stock.name][0]
            predict_stock.pp = (high + low + close) / 3
            predict_stock.sl = []
            predict_stock.sl.append((predict_stock.pp * 2) - high)
            predict_stock.sl.append(predict_stock.pp - (high - low))
            predict_stock.rl = []
            predict_stock.rl.append((predict_stock.pp * 2) - low)
            predict_stock.rl.append(predict_stock.pp + (high - low))
            logger.info(bold(predict_stock.name) + ': ' +
                             str([round(predict_stock.pp, 3),
                                  round(predict_stock.sl[0], 3),
                                  round(predict_stock.rl[0], 3)]))

    def isWorth(self, name):
        stock = [x.sl for x in self.predict_stocks if x.name == name][0]
        if self.graph.isDoji(name):
            for support in stock:
                if self.graph.isClose(name, support):
<<<<<<< HEAD
                    self.logger.info(
                        "It's worth to {mode} {product} on {price}"
=======
                    logger.info(
                        "It worth to {mode} {product} on {price}"
>>>>>>> ca1262a1e54b8ffe7a26f917818617247b219570
                        .format(mode=bold(green("buy")),
                                price=bold(support),
                                product=bold(name)))

    def start(self):
        self.graph.start()
        for y in range(2):
            time.sleep(65)
            self.getPivotPoints()
            for x in self.predict_stocks:
                self.isWorth(x.name)

    def stop(self):
        self.graph.stop()


class predictStock(object):
    def __init__(self, name):
        self.name = name
        self.prediction = 0
