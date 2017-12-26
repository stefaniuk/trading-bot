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
from ..patterns import Observable
from ..glob import Glob
from .utils import CommandPool, launch_thread

# exceptions
import tradingAPI.exceptions

# logging
import logging
logger = logging.getLogger('tradingbot.handler')
mov_log = logging.getLogger('mover')


class AbstractHandler(Observable):
    """abstract class"""
    def __init__(self):
        super().__init__()
        self.attach(Glob().tele)  # observers
        self.api = tradingAPI.API()
        self.pool = CommandPool()
        self.positions = []


class Handler(AbstractHandler):
    """Module to interact with the service"""
    def __init__(self):
        super().__init__()
        logger.debug("Handler initiated")

    def start(self):
        """start the handler"""
        logger.debug("starting handler")
        self.api.launch()
        creds = Glob().collection['main']['general']  # get credentials
        self.api.login(creds['username'], creds['password'])
        Thr = Thread(target=self.handle_pos)  # launch position handler
        launch_thread(Thr, 'handle_pos')
        Glob().events['HANDLEPOS_LIVE'].set()

    def stop(self):
        """stop the handler"""
        Glob().events['HANDLEPOS_LIVE'].clear()
        self.pool.close()  # closing pool
        self.api.logout()

    def get_pip(self, product):
        """get pip value of product"""
        pip = self.pool.wait_result(
            tradingAPI.utils.get_pip,
            kwargs={'api': self.api, 'name': product}, timeout=100)
        return pip

    def get_free_funds(self):
        """get free funds"""
        # time optimization
        if hasattr(self, 'last_free_funds'):
            if time.time() < self.last_free_funds[0] + 5:  # if < 5 sec elapsed
                return self.last_free_funds[1]  # get last result
        free = self.pool.wait_result(
            self.api.get_bottom_info, args=['free_funds'])
        self.last_free_funds = (time.time(), free)
        return free

    def update(self):
        """check positions and update"""
        self.old_pos = self.positions
        self.pool.wait_single_result(self.api.checkPos)
        # update positions
        self.positions.clear()
        for pos in self.api.positions:
            if not hasattr(pos, 'mov'):
                continue
            if not hasattr(pos.mov, 'unit_limit'):
                logger.debug("position has not unit_limit")
                continue
            self.positions.append(pos)

    def add_mov(self, product, mode, margin, stop_limit, secondary=None):
        """add movement with pool and api"""
        while margin > 0:
            used = self.pool.wait_result(
                self.api.addMov, args=[product], kwargs={
                    'mode': mode,
                    'auto_margin': margin,
                    'stop_limit': {
                        'gain': ['unit', stop_limit[0]],
                        'loss': ['unit', stop_limit[1]]}})
            if used == 0:
                return
            Glob().events['POS_LIVE'].set()
            self.notify_observers(event="auto-transaction", data={
                'product': product, 'mode': mode, 'quantity': used['quantity'],
                'margin': used['margin'], 'stop_limit': [stop_limit[0], stop_limit[1]]
                })
            if secondary is not None:  # if secondary product
                product = secondary
                margin -= used['margin']  # margin left
            else:
                margin = 0  # end cycle

    def check_positions(self):
        """check pos limit"""
        for pos in self.old_pos:
            if pos not in self.positions:
                self.notify_observers(event="close", data={
                    'product': pos.product, 'gain': pos.gain
                })
        for pos in self.positions:
            stk_ls = [x.stock for x in Glob().recorder.stocks
                      if x.product == pos.product or
                      pos.product in x.product][0]  # very ugly resolution
            if stk_ls.records:
                prices = stk_ls.records[-1]
            else:  # in case of cleared prices
                stk_prcs = [x for x in Glob().recorder.stocks
                            if x.product == pos.product or
                            pos.product in x.product][0].records[-1]
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
                    self.notify_observers(event="close", data={
                        'product': pos.product, 'gain': pos.gain
                    })
                    self.pool.wait_finish(pos.close)
                except tradingAPI.exceptions.PositionNotClosed:
                    logger.warning("position just closed by website client")

    def handle_pos(self):
        """handle positions (THREAD ONLY)"""
        while Glob().events['HANDLEPOS_LIVE'].wait(5):
            start = time.time()
            if Glob().events['POS_LIVE'].is_set():  # if launched
                old_pos_n = len(self.positions)
                self.update()
                self.check_positions()
                if old_pos_n > len(self.positions) == 0:
                    Glob().events['POS_LIVE'].clear()
            time.sleep(max(0, 1 - (time.time() - start)))
