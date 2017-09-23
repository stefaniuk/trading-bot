import time
import os.path
from threading import Thread
from .color import *
from .logger import *
from ..core import events
from ..configurer import Configurer
from .stocks import PredictStockScalping
from .grapher import Grapher
from .handler import Handler


class Calculator(object):
    """namespace for complex predictive functions"""
    def __init__(self, p_stock, graph):
        self.name = p_stock.name
        self.graph = graph
        self.emas = []

    def __clear(self):
        self.emas = self.emas[:50]

    def sma(self, periods, unit=1):
        """calculate the Simple Moving Average"""
        periods *= unit
        records = [x.records for x in self.graph.stocks
                   if x.name == self.name][0]
        close_list = [x[-1] for x in records[-periods:]]
        return sum(close_list) / len(close_list)

    def ema(self, periods, unit=1):
        """calculate the Exponential Moving Average"""
        records = [x.records for x in self.graph.stocks
                   if x.name == self.name][0]
        close = records[-1][-1]
        multiplier = 2 / (periods + 1)
        if len(self.emas) == 0:
            latest_ema = close
        else:
            latest_ema = self.emas[-1]
        ema = (close - latest_ema) * multiplier + latest_ema
        self.emas.append(ema)
        return ema

    def stochastic_oscillator_5_3_3(self, k_fast_list, k_list):
        """calculate the Stochastic Oscillator 5 3 3"""
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
    """abstract class for algorithm"""
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
        """start the handlers and the run function"""
        T3 = Thread(target=self.graph.start)
        T4 = Thread(target=self.handler.start)
        T5 = Thread(target=self.run, args=(sleep_time,))
        T5.deamon = True
        T3.start()
        T4.start()
        T3.join()
        T4.join()
        time.sleep(65)
        T5.start()
        logger.debug("Pivoting thread #5 launched")

    def stop(self):
        """stop all handlers"""
        self.graph.stop()
        self.handler.stop()

# DEPRECATED
# class Pivot(BaseAlgorithm):
#     def __init__(self, conf):
#         super().__init__(conf)
#         logger.debug("Pivot algortihm initialized")
#
#     def getPivotPoints(self):
#         for stock in self.graph.stocks:
#             high = max([float(x[1]) for x in stock.records])
#             low = min([float(x[2]) for x in stock.records])
#             close = [float(x[3]) for x in stock.records][-1]
#             logger.debug(f"price: {close}")
#             if stock not in [x.candlestick for x in self.stocks]:
#                 self.stocks.append(PredictStock(stock))
#             p_stock = [x for x in self.stocks if x.candlestick == stock][0]
#             p_stock.pp = (high + low + close) / 3
#             p_stock.sl = []
#             p_stock.sl.append((p_stock.pp * 2) - high)
#             p_stock.sl.append(p_stock.pp - (high - low))
#             p_stock.rl = []
#             p_stock.rl.append((p_stock.pp * 2) - low)
#             p_stock.rl.append(p_stock.pp + (high - low))
#
#     def isWorth(self, name):
#         stock = [x for x in self.stocks if x.name == name][0]
#         stock.prediction = 0
#         s = self.strategy
#         for val in s['sentiment_ini']:
#             if stock.candlestick.sentiment >= val[0]:
#                 stock.add(val[1])
#         for support in stock.sl:
#             logger.debug(f"support: {support}")
#             if self.graph.isClose(name, support):
#                 stock.add(s['support'])
#                 if self.graph.isDoji(name):
#                     stock.add(s['doji'])
#         stock.multiply(stock.candlestick.sentiment*s['sentiment_mult'])
#         logger.debug(f"sentiment: {bold(stock.candlestick.sentiment)}")
#         logger.info(f"It's worth to {bold(green('buy'))} " +
#                     f"{bold(name)} on {bold(blue(stock.prediction))}")
#         return stock.prediction
#
#     def run(self):
#         while events.LIVE.wait(5):
#             self.getPivotPoints()
#             for x in self.stocks:
#                 pred = self.isWorth(x.name)
#                 if pred >= self.strategy['prediction']:
#                     self.handler.addMov(x.name, pred)
#             events.LIVE.wait_terminate(60)


class Scalper(BaseAlgorithm):
    """Scalper algorithm class"""
    def __init__(self, conf):
        super().__init__(conf)
        logger.debug("Scalper algortihm initialized")

    def _get_margin(self):
        margin = ((self.handler.api.get_bottom_info('free_funds') *
                   self.strategy['max_margin_risk'])
                  / self.strategy['max_trans'])
        return margin

    def work(self):
        """update the predict stocks list"""
        for stock in self.graph.stocks:
            if stock not in [x.candlestick for x in self.stocks]:
                self.stocks.append(PredictStockScalping(stock))
                p_stock = [x for x in self.stocks if x.candlestick == stock][0]
                p_stock.calculator = Calculator(p_stock, self.graph)
            else:
                p_stock = [x for x in self.stocks if x.candlestick == stock][0]
            p_stock.prediction = 0
            p_stock.ema_50 = p_stock.calculator.ema(50)
            p_stock.ema_100 = p_stock.calculator.ema(100)
            p_stock.price = [x.vars for x in self.graph.api.stocks
                             if x.name == stock.name][0][-1][0]
            try:
                momentum = p_stock.calculator.stochastic_oscillator_5_3_3(
                    p_stock.k_fast_list, p_stock.k_list)
            except ZeroDivisionError:
                logger.warning("momentum: highest price equal to lowest price")
                momentum = None
            logger.debug(f"Price: {bold(p_stock.price)}")
            logger.debug(f"EMA 50: {bold(p_stock.ema_50)}")
            logger.debug(f"EMA 100: {bold(p_stock.ema_100)}")
            logger.debug(f"Momentum: {bold(momentum)}")
            p_stock.momentum.append(momentum)
            p_stock.margin = self._get_margin()
            p_stock.clear()

    def worth(self, stock):
        """check if it's worth to place a movement"""
        if (stock.ema_50 > stock.ema_100 and
                stock.price < stock.ema_100 and stock.mom_up()):
            stock.mode = 'buy'
            logger.info(f"It's profitable to {bold('buy')} {stock.name}")
            return True
        elif (stock.ema_50 < stock.ema_100 and
              stock.price > stock.ema_100 and stock.mom_down()):
            stock.mode = 'sell'
            logger.info(f"It's profitable to {bold('buy')} {stock.name}")
            return True
        else:
            return False

    def run(self, time=1):
        """main run function, here it is the pivot of the algorithm"""
        while events.LIVE.wait(5):
            old_stock_n = self.graph.count
            self.work()
            time -= 1
            if time < 0:
                for x in self.stocks:
                    if self.worth(x):
                        self.handler.addMov(x.name, 30, 10,
                                            x.margin, mode=x.mode)
                    if x.name.lower() == 'eur/usd zero':
                        self.handler.addMov(x.name, 30, 10,
                                            x.margin, mode='buy')
            while self.graph.count == old_stock_n:
                if events.LIVE.is_set():
                    events.LIVE.wait_terminate(1)
                else:
                    break
