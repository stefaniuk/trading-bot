# -*- coding: utf-8 -*-

"""
tradingbot.core.handler
~~~~~~~~~~~~~~

This module provides handler object that manipulates
real account and place movements.
"""

import time
import tradingAPI
from threading import Thread
from ..glob import Glob
from .utils import CommandPool
# from .stocks import StockAnalysis
# from .utils import (conv_limit, who_closest, ApiSupp, Movement,
#                     CommandPool, eval_earn)
# from ..core import events

# logging
import logging
logger = logging.getLogger('tradingbot.handler')


class Handler(object):
    """Module to interact with the broker"""
    def __init__(self):
        self.api = tradingAPI.API()
        self.pool = CommandPool()
        self.stocks = []
        self.positions = []
        logger.debug("Handler initiated")

    def start(self):
        """start the handler"""
        logger.debug("starting handler")
        self.api.launch()
        # get credentials
        creds = Glob().collection['main']['general']
        self.api.login(creds['username'], creds['password'])
        # self.start_handlePos()
        # logger.debug("Thread #3 launched - handlePos updater")
        # events.POSHANDLER.set()

    def stop(self):
        """stop the handler"""
        Glob().events['HAND_LIVE'].clear()
        self.api.logout()

    def get_pip(self, product):
        """get pip value of product"""
        pip = self.pool.add_and_wait(
            tradingAPI.utils.get_pip,
            kwargs={'api': self.api, 'name': product}, timeout=100)
        return pip

    # def _find_mov(self, prod, price):
    #     """find movement by prod and price"""
    #     mov_len = [x for x in self.positions
    #                if x.product == prod]
    #     if len(mov_len) == 0:
    #         return None
    #         logger.debug("hanlder._find_mov returned None")
    #         logger.debug(f"handler._find_mov:product: prod")
    #     elif len(mov_len) == 1:
    #         return mov_len[0]
    #     elif len(mov_len) > 1:
    #         closest_price = 0
    #         for mov in mov_len:
    #             closest_price = who_closest(price, closest_price, mov.price)
    #         return [x for x in mov_len if x.price == closest_price][0]
    #
    # def update(self):
    #     """check positions and update"""
    #     self.pool.add_and_wait_single(self.api.checkPos)
    #     for mov in self.api.movements:
    #         movs = [x for x in self.positions if x.id == mov.id]
    #         if not movs:
    #             mov_fnd = self._find_mov(mov.product, mov.price)
    #             if mov_fnd is None:
    #                 logger.debug(
    #                     f"movement not hanlded by bot {mov.product}")
    #                 continue
    #         else:
    #             mov_fnd = movs[0]
    #         mov_fnd.update(mov)
    #     logger.debug("updated positions")
    #
    # def checkMovs(self):
    #     pos_list = [x for x in self.positions
    #                 if x.gain is not None or x.loss is not None
    #                 and hasattr(x, 'curr')]
    #     for pos in pos_list:
    #         logger.debug(f"{pos.product} gain: {pos.gain} - loss: {pos.loss}")
    #         if pos.mode == 'buy':
    #             mode = (pos.curr <= pos.price - pos.loss or
    #                     pos.curr >= pos.price + pos.gain)
    #         elif pos.mode == 'sell':
    #             mode = (pos.curr >= pos.price + pos.loss or
    #                     pos.curr <= pos.price - pos.gain)
    #         if mode:
    #             logger.debug(f"mode: {pos.mode}, curr: {pos.curr}, " +
    #                          f"price: {pos.price}")
    #             earnings = eval_earn(pos.quantity, pos.curr,
    #                                  pos.price, pos.mode)
    #             logger.info(f"{blue('closing')} {bold(pos.product)} " +
    #                         f"at {bold(pos.curr)} with a revenue of " +
    #                         f"{bold(earnings)}")
    #             if self.pool.add_and_wait(self.api.closeMov, args=[pos.id]):
    #                 self.positions.remove(pos)
    #
    # def handlePos(self):
    #     """postition handler"""
    #     while events.POSHANDLER.wait(5):
    #         while len(self.positions) == 0:
    #             time.sleep(1)
    #         self.update()
    #         self.checkMovs()
    #
    # def start_handlePos(self):
    #     """start the hanlder"""
    #     T3 = Thread(target=self.handlePos)
    #     T3.daemon = True
    #     T3.start()
    #
    # def addMov(self, prod, gain, loss, margin, mode="buy"):
    #     """add a movement (short or long) of a product with stop limit of pip
    #      (gain or loss), it can also accept margin to auto define the
    #      quantity"""
    #     price = [x.vars[-1][0] for x in Glob().recorder.api.stocks
    #              if x.name == prod][0]
    #     if not [x for x in self.stocks if x.name == prod]:
    #         self.stocks.append(StockAnalysis(prod))
    #     stock = [x for x in self.stocks if x.name == prod][0]
    #     gain, loss = conv_limit(gain, loss, stock.name)
    #     stop_limit = {'mode': 'unit', 'value': (gain, loss)}
    #     free_funds = self.pool.add_and_wait(self.api.get_bottom_info,
    #                                         args=['free_funds'])
    #     logger.debug(f"free funds: {free_funds}")
    #     mov_results = self.pool.add_and_wait(
    #         self.api.addMov,
    #         args=[prod], kwargs={'mode': mode, 'stop_limit': stop_limit,
    #                              'auto_quantity': margin})
    #     isint = isinstance({}, type(mov_results))
    #     if isint:
    #         self.positions.append(
    #             Movement(mov_results['name'], gain=gain, loss=loss, mode=mode,
    #                      margin=margin, price=price))
    #         marg_used = mov_results['margin']
    #         margin -= marg_used
    #     insfunds = mov_results == 'INSFU'
        # if (isint or insfunds) and self.strategy.get('secondary-prefs'):
        #     if self.strategy['secondary-prefs'].get(prod):
        #         new_prod = self.strategy['secondary-prefs'][prod]
        #         logger.debug(f"Buying more {new_prod}")
        #         unit_value = self.pool.add_and_wait(self.supp.get_unit_value,
        #                                             args=[new_prod])
        #         quant = margin // unit_value
        #         logger.debug(f"{new_prod} {quant} - {margin} : {unit_value}")
        #         new_mov_results = self.pool.add_and_wait(
        #             self.api.addMov,
        #             args=[new_prod], kwargs={'quantity': quant, 'mode': mode,
        #                                      'stop_limit': stop_limit,
        #                                      'name_counter': prod})
        #         self.positions.append(
        #             Movement(new_mov_results['name'], quant=quant, gain=gain,
        #                      loss=loss, mode=mode, margin=margin, price=price))

    # def closeAll(self):
    #     """close all movements"""
    #     self.update()
    #     for mov in self.api.movements:
    #         self.api.closeMov(mov.id)
