from tradingAPI import API
from .color import *
from .logger import *
from .data import pip_table
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

    def __conv_limit(self, gain, loss, name):
        try:
            pip = pip_table[name.split(' ')[0]]
        except Exception:
            logger.error("conv_limit failed, sorry for the unstable function")
            logger.debug(name)
            raise
        gain *= pip
        loss *= pip
        return gain, loss

    def _get_limit(self, margin, volatility):
        mult = self.strategy['stop_limit']
        res = margin * volatility * mult / 10
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

    def addMov(self, prod, gain, loss, margin, mode="buy"):
        price = [x.vars[-1][0] for x in self.graphapi.stocks
                 if x.name == prod][0]
        if not [x for x in self.analysis if x.name == prod]:
            self.analysis.append(StockAnalysis(prod))
        stock = [x for x in self.analysis if x.name == prod][0]
        gain, loss = self.__conv_limit(gain, loss, stock.name)
        stop_limit = {'mode': 'unit', 'value': (gain, loss)}
        free_funds = self.api.get_bottom_info('free_funds')
        logger.debug(f"free funds: {free_funds}")
        result = self.api.addMov(
            prod, mode=mode, stop_limit=stop_limit, auto_quantity=margin)
        if isinstance(int(), type(result)):
            if result > 0:
                margin -= result
        if isinstance(int(), type(result)) or result == 'INSFU':
            prod = prod.split(' ')[0]
            self.api.addMov(
                prod, mode=mode, stop_limit=stop_limit, auto_quantity=margin)

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
