from tradingAPI import API
from .logger import *
from .stocks import StockAnalysis


class Handler(object):
    '''Module to interact with the broker'''
    def __init__(self, conf, strategy, graph):
        self.config = conf
        self.strategy = strategy
        self.api = API(self.config.config['logger_level'])
        self.analysis = []
        self.graph = graph
        self.graphapi = graph.api

    def _get_limit(self, margin, volatility):
        mult = self.strategy['stop-limit']
        res = (margin * (volatility / 10)) * mult
        return res

    def run(self):
        '''to write'''
        pass

    def start(self):
        logger.debug("starting handler")
        self.api.launch()
        self.api.start()

    def stop(self):
        self.api.logout()

    def addMov(self, prod):
        price = [x.vars[-1][0] for x in self.graphapi.stocks
                 if x.name == prod][0]
        if not [x for x in self.analysis if x.name == prod]:
            self.analysis.append(StockAnalysis(prod))
        stock = [x for x in self.analysis if x.name == prod][0]
        records = [x.records for x in self.graph.stocks
                   if x.name == prod][0][:self.strategy['max_records']]
        mx = max([x[1] for x in records])
        mn = min([x[2] for x in records])
        stock.volatility = mx - mn
        margin = 100 / self.strategy['max_trans'] / 100 * \
            (self.api.get_bottom_info('free_funds') *
             self.strategy['max_margin_risk'])
        limit = self._get_limit(margin, stock.volatility)
        stop_limit = {'gain': ['value', limit],
                      'loss': ['value', limit]}
        free_funds = self.api.get_bottom_info('free_funds')
        self.api.addMov(prod, stop_limit=stop_limit, auto_quantity=margin)
