from tradingAPI import API
from .color import *
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
        logger.debug("Handler initialized")

    def _get_limit(self, margin, volatility):
        mult = self.strategy['stop_limit']
        res = (margin * (volatility / 10)) * mult
        return res

    def start(self):
        logger.debug("starting handler")
        self.api.launch()
        creds = self.config.config['general']
        if not self.api.login(creds['username'], creds['password']):
            logger.critical("hanlder failed to start")
            self.stop()

    def stop(self):
        self.api.logout()

    def addMov(self, prod, pred):
        price = [x.vars[-1][0] for x in self.graphapi.stocks
                 if x.name == prod][0]
        logger.debug(f"price: {price}")
        if not [x for x in self.analysis if x.name == prod]:
            self.analysis.append(StockAnalysis(prod))
        stock = [x for x in self.analysis if x.name == prod][0]
        records = [x.records for x in self.graph.stocks
                   if x.name == prod][0][-self.strategy['max_records']:]
        mx = max([float(x[1]) for x in records])
        mn = min([float(x[2]) for x in records])
        logger.debug(f"max: {mx}\nmin: {mn}")
        stock.volatility = mx - mn
        logger.debug(f"volatility: {stock.volatility}")
        pred_cal = self.strategy['prediction']
        margin = 100 / self.strategy['max_trans'] / 100 * \
            ((pred - pred_cal) * self.strategy['pred_mult'] + 100) * \
            (self.api.get_bottom_info('free_funds') *
             self.strategy['max_margin_risk'])
        logger.debug(f"margin: {margin}")
        limit = self._get_limit(margin, stock.volatility)
        logger.debug(f"limit: {limit}")
        stop_limit = {'mode': 'value', 'value': limit}
        free_funds = self.api.get_bottom_info('free_funds')
        logger.debug(f"free funds: {free_funds}")
        self.api.addMov(prod, stop_limit=stop_limit, auto_quantity=margin)

    def closeMov(self):
        pass
