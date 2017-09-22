# -*- coding: utf-8 -*-

"""
tradingbot.core.handler
~~~~~~~~~~~~~~

This module provides handler object that manipulates
real account and place movements.
"""

import tradingAPI
from .color import *
from .logger import logger
from .stocks import StockAnalysis
from .utils import _conv_limit, ApiSupp


class Handler(object):
    """Module to interact with the broker"""
    def __init__(self, conf, strategy, graph):
        self.config = conf
        self.strategy = strategy
        self.api = tradingAPI.API(conf.config['logger_level_api'])
        self.supp = ApiSupp(graph.api)
        self.graph = graph
        self.stocks = []
        logger.debug("Handler initialized")

    # DEPRECATED
    # def _get_limit(self, margin, volatility):
    #     mult = self.strategy['stop_limit']
    #     res = margin * volatility * mult / 10
    #     return res

    def start(self):
        """start the handler"""
        logger.debug("starting handler")
        self.api.launch()
        creds = self.config.config['general']
        if not self.api.login(creds['username'], creds['password']):
            logger.critical("hanlder failed to start")
            self.stop()

    def stop(self):
        """stop the handler"""
        self.api.logout()

    def update(self):
        """check positions and update"""
        self.api.checkPos()

    def addMov(self, prod, gain, loss, margin, mode="buy"):
        """add a movement (short or long) of a product with stop limit of pip
         (gain or loss), it can also accept margin to auto define the
         quantity"""
        price = [x.vars[-1][0] for x in self.graph.api.stocks
                 if x.name == prod][0]
        if not [x for x in self.stocks if x.name == prod]:
            self.stocks.append(StockAnalysis(prod))
        stock = [x for x in self.stocks if x.name == prod][0]
        gain, loss = _conv_limit(gain, loss, stock.name)
        stop_limit = {'mode': 'unit', 'value': (gain, loss)}
        free_funds = self.api.get_bottom_info('free_funds')
        logger.debug(f"free funds: {free_funds}")
        result = self.api.addMov(
            prod, mode=mode, stop_limit=stop_limit, auto_quantity=margin)
        if isinstance(0.0, type(result)):
            margin -= result
        isint = isinstance(0.0, type(result))
        insfunds = result == 'INSFU'
        if isint or insfunds and self.strategy.get('secondary-prefs'):
            prod = self.strategy['secondary-prefs'][prod]
            unit_value = self.supp.get_unit_value(prod)
            quant = margin // unit_value
            self.api.addMov(
                prod, quantity=quant, mode=mode, stop_limit=stop_limit)

    def closeMov(self, product, quantity=None, price=None):
        """close a movement by name and quantity (or price).
         Needs an upgrade"""
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
        """close all movements"""
        self.update()
        for mov in self.api.movements:
            self.api.closeMov(mov.id)
