import time
import os.path
from threading import Thread
from .color import *
from .logger import *
from ..configurer import Configurer
from .stocks import PredictStock
from .grapher import Grapher


class BaseAlgorithm(object):
    def __init__(self, conf):
        self.conf = conf
        self.graph = Grapher(self.conf)
        self.stocks = []

    def stop(self):
        self.graph.stop()


class Pivot(BaseAlgorithm):
    def __init__(self, conf):
        super().__init__(conf)
        strat_conf = Configurer(os.path.join(
            os.path.dirname(__file__), 'strategies',
            self.conf.config['strategy']['strategy'] + '.yml'))
        strat_conf.read()
        self.strategy = strat_conf.config
        logger.debug("Pivot algortihm initialized")
    
    def getPivotPoints(self):
        for stock in self.graph.stocks:
            high = max([float(x[1]) for x in stock.records])
            low = min([float(x[2]) for x in stock.records])
            close = [float(x[3]) for x in stock.records][-1]
            if stock not in [x.candlestick for x in self.stocks]:
                self.stocks.append(PredictStock(stock))
            p_stock = [x for x in self.stocks if x.candlestick == stock][0]
            p_stock.pp = (high + low + close) / 3
            p_stock.sl = []
            p_stock.sl.append((p_stock.pp * 2) - high)
            p_stock.sl.append(p_stock.pp - (high - low))
            p_stock.rl = []
            p_stock.rl.append((p_stock.pp * 2) - low)
            p_stock.rl.append(p_stock.pp + (high - low))

    def isWorth(self, name):
        stock = [x for x in self.stocks if x.name == name][0]
        stock.prediction = 0
        s = self.strategy
        for val in s['sentiment_ini']:
            if stock.candlestick.sentiment >= val[0]:
                stock.add(val[1])
        for support in stock.sl:
            if self.graph.isClose(name, support):
                stock.add(s['support'])
        if self.graph.isDoji(name):
            stock.add(s['doji'])
        stock.multiply(stock.candlestick.sentiment*s['sentiment_mult'])
        logger.debug(f"sentiment: {bold(stock.candlestick.sentiment)}")
        logger.info(f"It's worth to {bold(green('buy'))} " +
            f"{bold(name)} on {bold(blue(stock.prediction))}")

    def run(self):
        while self.graph.live.wait(10):
            self.getPivotPoints()
            for x in self.stocks:
                self.isWorth(x.name)
            self.graph._waitTerminate(60)

    def start(self):
        self.graph.start()
        T3 = Thread(target=self.run)
        T3.deamon = True
        time.sleep(65)
        T3.start()
        logger.debug("Pivoting thread #3 launched")
