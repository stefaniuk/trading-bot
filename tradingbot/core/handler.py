# -*- coding: utf-8 -*-

"""
tradingbot.core.handler
~~~~~~~~~~~~~~

This module provides handler object that manipulates
real account and place movements.
"""

import time
import tradingAPI
from threading import Thread, active_count
from ..glob import Glob
from .utils import CommandPool

# exceptions
import tradingAPI.exceptions

# logging
import logging
logger = logging.getLogger('tradingbot.handler')
mov_log = logging.getLogger('mover')


class Handler(object):
    """Module to interact with the broker"""
    def __init__(self):
        self.api = tradingAPI.API()
        self.pool = CommandPool()
        self.positions = []
        logger.debug("Handler initiated")

    def start(self):
        """start the handler"""
        logger.debug("starting handler")
        self.api.launch()
        # get credentials
        creds = Glob().collection['main']['general']
        self.api.login(creds['username'], creds['password'])
        Thr = Thread(target=self.handle_pos)
        Thr.daemon = True
        Thr.start()
        Glob().events['HANDLEPOS_LIVE'].set()
        logger.debug("Thread #%d launched - handle_pos launched" %
                     active_count())

    def stop(self):
        """stop the handler"""
        Glob().events['HANDLEPOS_LIVE'].clear()
        # complete pool
        timeout = time.time() + 10
        while time.time() < timeout:
            if self.pool.pool:
                time.sleep(1)
            else:
                break
        self.api.logout()

    def get_pip(self, product):
        """get pip value of product"""
        pip = self.pool.add_and_wait(
            tradingAPI.utils.get_pip,
            kwargs={'api': self.api, 'name': product}, timeout=100)
        return pip

    def get_free_funds(self):
        """get free funds"""
        return self.pool.add_and_wait(
            self.api.get_bottom_info, args=['free_funds'])

    def update(self):
        """check positions and update"""
        self.pool.add_and_wait_single(self.api.checkPos)
        # update positions
        self.positions.clear()
        for pos in self.api.positions:
            if not hasattr(pos, 'mov'):
                # removed for spam
                # logger.debug("position not handled by handler")
                continue
            if not hasattr(pos.mov, 'unit_limit'):
                logger.debug("position has not unit_limit")
                continue
            self.positions.append(pos)

    def add_mov(self, product, mode, margin, stop_limit):
        """add movement with pool and api"""
        self.pool.add_waituntil(self.api.addMov, args=[product], kwargs={
            'mode': mode,
            'auto_margin': margin,
            'stop_limit': {
                'gain': ['unit', stop_limit[0]],
                'loss': ['unit', stop_limit[1]]}})
        Glob().events['POS_LIVE'].set()

    def check_positions(self):
        """check pos limit"""
        for pos in self.positions:
            stk_ls = [x.stock for x in Glob().recorder.stocks
                      if x.product == pos.product][0]
            if stk_ls.records:
                prices = stk_ls.records[-1]
            # in case of cleared prices
            else:
                stk_prcs = [x for x in Glob().recorder.stocks
                            if x.product == pos.product][0].records[-1]
                prices = [stk_prcs[0][-1], stk_prcs[1][-1]]
            if pos.mode == 'buy':
                trigger = (
                    prices[0] >= pos.mov.buy_price + pos.mov.unit_limit[0] or
                    prices[1] <= pos.mov.sell_price - pos.mov.unit_limit[1])
            elif pos.mode == 'sell':
                trigger = (
                    prices[1] <= pos.mov.sell_price - pos.mov.unit_limit[0] or
                    prices[0] >= pos.mov.buy_price + pos.mov.unit_limit[1])
            if trigger:
                mov_log.info("closing %s" % pos.product)
                try:
                    self.pool.add_waituntil(pos.close)
                except tradingAPI.exceptions.PositionNotClosed:
                    logger.warning("position just closed by website client")

    def handle_pos(self):
        """handle positions"""
        while Glob().events['HANDLEPOS_LIVE'].wait(5):
            start = time.time()
            # if launched
            if Glob().events['POS_LIVE'].is_set():
                self.update()
                if len(self.positions) == 0:
                    Glob().events['POS_LIVE'].clear()
                self.check_positions()
            time.sleep(max(0, 1 - (time.time() - start)))

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
