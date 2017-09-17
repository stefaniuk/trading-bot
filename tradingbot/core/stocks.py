class BaseStock(object):
    def __init__(self, name):
        self.name = name
        self.records = []


class CandlestickStock(BaseStock):
    def __init__(self, name):
        super().__init__(name)
        self.sentiment = None

    def addRecord(self, openstock, maxstock, minstock, closestock):
        self.records.append([openstock, maxstock, minstock, closestock])


class PredictStock(BaseStock):
    def __init__(self, candlestick):
        super().__init__(candlestick.name)
        self.candlestick = candlestick
        self.prediction = 0

    def add(self, val):
        self.prediction += (val * (1 - self.prediction))

    def multiply(self, val):
        self.prediction *= val
        if self.prediction > 1:
            self.prediction = 1


class PredictStockScalping(PredictStock):
    def __init__(self, candlestick):
        super().__init__(candlestick)
        self.momentum = []
        self.k_fast_list = []
        self.k_list = []

    def clear(self):
        self.momentum = self.momentum[-2:]
        self.k_fast_list = self.k_fast_list[-3:]
        self.k_list = self.k_list[-3:]

    def mom_up(self):
        if len(self.momentum) < 2:
            return False
        if self.momentum[-2] <= 20 < self.momentum[-1]:
            return True
        else:
            return False

    def mom_down(self):
        if len(self.momentum) < 2:
            return False
        if self.momentum[-2] >= 80 > self.momentum[-1]:
            return True
        else:
            return False


class StockAnalysis(object):
    def __init__(self, name):
        self.name = name
        self.volatility = None
