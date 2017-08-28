import asyncio

from .grapher import Grapher

class Pivot(object):
    def __init__(self, api, conf):
        self.api = api
        self.conf = conf
        self.graph = Grapher(self.conf)
        self.graph.update = asyncio.gather(self.graph.updatePrice(), self.graph.candlestickUpdate())

    def getPivotPoint(self):
        self.graph


class trueStock(object):
    def __init__(self, name):
        self.name = name
        