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

    def update(self):
        self.api.checkPos()

    def addMov(self, prod, pred):
        price = [x.vars[-1][0] for x in self.graphapi.stocks
                 if x.name == prod][0]
        if not [x for x in self.analysis if x.name == prod]:
            self.analysis.append(StockAnalysis(prod))
        stock = [x for x in self.analysis if x.name == prod][0]
        records = [x.records for x in self.graph.stocks
                   if x.name == prod][0][-self.strategy['max_records']:]
        mx = max([float(x[1]) for x in records])
        mn = min([float(x[2]) for x in records])
        stock.volatility = mx - mn
        logger.debug(f"volatility: {stock.volatility}")
        pred_cal = self.strategy['prediction']
        margin = 100 / self.strategy['max_trans'] / 100 * \
            ((pred - pred_cal) * self.strategy['pred_mult'] + 100) * \
            (self.api.get_bottom_info('free_funds') *
             self.strategy['max_margin_risk'])
        limit = self._get_limit(margin, stock.volatility)
        stop_limit = {'mode': 'value', 'value': limit}
        free_funds = self.api.get_bottom_info('free_funds')
        logger.debug(f"free funds: {free_funds}")
        self.api.addMov(prod, stop_limit=stop_limit, auto_quantity=margin)

    def closeMov(self, product, quantity=None, price=None):
        self.update()
        mvs = [x for x in self.api.movements if x.product == product]
        if quantity is not None:
            mvs = [x for x in movs if x.quantity == quantity]
        if price is not None:
            mvs = [x for x in movs if x.price == price]
        count = 0
        earn = 0
        for x in mvs:
            if self.api.closeMov(x.id):
                count += 1
                earn += x.earn
        logger.info(f"closed {bold(count)} movements of {bold(product)} " +
                    f"with a revenue of {bold(green(earn))}")

    def closeAll(self):
        self.update()
        for mov in self.api.movements:
            self.api.closeMov(mov.id)
