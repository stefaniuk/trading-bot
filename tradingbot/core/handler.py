from tradingAPI import API
from .logger import *


class Handler(object):
    '''Module to interact with the broker'''
    def __init__(self, conf, strategy):
        self.config = conf
        self.strategy = strategy
        self.api = API(self.config.config['logger_level'])

    def run(self):
        '''to write'''
        pass

    def start(self):
        logger.debug("starting handler")
        self.api.launch()
        self.api.start()

    def stop(self):
        self.api.logout()

    def addMov(self, prod, quant, mode):
        self.api.addMov(
            product=prod,
            quantity=quant,
            mode=mode,
            stop_limit=self.strategy['stop_limit'])