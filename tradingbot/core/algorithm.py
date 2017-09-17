import time
import os.path
from threading import Thread
from .color import *
from .logger import *
from ..configurer import Configurer
from .stocks import PredictStockScalping
from .grapher import Grapher
from .handler import Handler


class Calculator(object):
    def __init__(self, p_stock, graph):
        self.name = p_stock.name
        self.graph = graph
        self.emas = []

    def __clear(self):
        self.emas = self.emas[:50]

    def sma(self, periods, unit=1):
        periods *= unit
        records = [x.records for x in self.graph.stocks
                   if x.name == self.name][0]
        close_list = [x[-1] for x in records[-periods:]]
        return sum(close_list) / len(close_list)

    def ema(self, periods, unit=1):
        records = [x.records for x in self.graph.stocks
                   if x.name == self.name][0]
        close = records[-1][-1]
        print(close)
        multiplier = 2 / (periods + 1)
        print(multiplier)
        if len(self.emas) == 0:
            latest_ema = close
        else:
            latest_ema = self.emas[-1]
        print(latest_ema)
        ema = (close - latest_ema) * multiplier + latest_ema
        print(ema)
        self.emas.append(ema)
        return ema

    def stochastic_oscillator_5_3_3(self, k_fast_list, k_list):
        records = [x.records for x in self.graph.stocks
                   if x.name == self.name][0][-5:]
        close = records[-1][-1]
        highest_high = max([x[1] for x in records])
        lowest_low = min([x[2] for x in records])
        k_fast = (close - lowest_low) / (highest_high - lowest_low) * 100
        k_fast_list.append(k_fast)
        k = sum(k_fast_list[-3:]) / 3
        k_list.append(k)
        d = sum(k_list[-3:]) / 3
        return d


class BaseAlgorithm(object):
    '''abstract class for algorithm'''
    def __init__(self, conf):
        # check strategy
        strat_conf = Configurer(os.path.join(
            os.path.dirname(__file__), 'strategies',
            conf.config['strategy']['strategy'] + '.yml'))
        strat_conf.read()
        self.strategy = strat_conf.config
        self.conf = conf
        self.graph = Grapher(self.conf, self.strategy)
        self.handler = Handler(self.conf, self.strategy, self.graph)
        self.stocks = []

    def start(self, sleep_time=0):
        T3 = Thread(target=self.graph.start)
        T4 = Thread(target=self.handler.start)
        T5 = Thread(target=self.run)
        T5.deamon = True
        T3.start()
        T4.start()
        T3.join()
        T4.join()
        time.sleep(sleep_time)
        T5.start()
        logger.debug("Pivoting thread #5 launched")

    def stop(self):
        self.graph.stop()
        self.handler.stop()


class Pivot(BaseAlgorithm):
    def __init__(self, conf):
        super().__init__(conf)
        logger.debug("Pivot algortihm initialized")

    def getPivotPoints(self):
        for stock in self.graph.stocks:
            high = max([float(x[1]) for x in stock.records])
            low = min([float(x[2]) for x in stock.records])
            close = [float(x[3]) for x in stock.records][-1]
            logger.debug(f"price: {close}")
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
            logger.debug(f"support: {support}")
            if self.graph.isClose(name, support):
                stock.add(s['support'])
                if self.graph.isDoji(name):
                    stock.add(s['doji'])
        stock.multiply(stock.candlestick.sentiment*s['sentiment_mult'])
        logger.debug(f"sentiment: {bold(stock.candlestick.sentiment)}")
        logger.info(f"It's worth to {bold(green('buy'))} " +
                    f"{bold(name)} on {bold(blue(stock.prediction))}")
        return stock.prediction

    def run(self):
        while self.graph.live.wait(5):
            self.getPivotPoints()
            for x in self.stocks:
                pred = self.isWorth(x.name)
                if pred >= self.strategy['prediction']:
                    self.handler.addMov(x.name, pred)
            self.graph._waitTerminate(60)


class Scalper(BaseAlgorithm):
    '''Scalper algorithm class'''
    def __init__(self, conf):
        super().__init__(conf)
        logger.debug("Scalper algortihm initialized")

    def work(self):
        for stock in self.graph.stocks:
            if stock not in [x.candlestick for x in self.stocks]:
                self.stocks.append(PredictStockScalping(stock))
                p_stock = [x for x in self.stocks if x.candlestick == stock][0]
                p_stock.calculator = Calculator(p_stock, self.graph)
            else:
                p_stock = [x for x in self.stocks if x.candlestick == stock][0]
            p_stock.prediction = 0
            ema_50 = p_stock.calculator.ema(50)
            ema_100 = p_stock.calculator.ema(100)
            price = [x.vars for x in self.graph.api.stocks
                     if x.name == stock.name][0][-1][0]
            momentum = p_stock.calculator.stochastic_oscillator_5_3_3(
                p_stock.k_fast_list, p_stock.k_list)
            logger.debug(f"Price: {bold(price)}")
            logger.debug(f"EMA 50: {bold(ema_50)}")
            logger.debug(f"EMA 100: {bold(ema_100)}")
            logger.debug(f"Momentum: {bold(momentum)}")
            p_stock.momentum.append(momentum)
            p_stock.clear()
            if (ema_50 > ema_100 and price < ema_100 and p_stock.mom_up()):
                p_stock.prediction = 1
                logger.info(f"It's profitable to {bold('buy')} {p_stock.name}")
            else:
                p_stock.prediction = 0

    def run(self):
        while self.graph.live.wait(5):
            old_stock_n = self.graph.count
            self.work()
            for x in self.stocks:
                if x.prediction is True:
                    self.handler.addMov(x.name, 30, 10)
            while self.graph.count == old_stock_n:
                if not self.graph._waitTerminate(1):
                    break
