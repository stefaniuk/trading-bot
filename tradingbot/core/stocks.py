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