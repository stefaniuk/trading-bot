# -*- coding: utf-8 -*-

"""
tradingbot.core.exceptions
~~~~~~~~~~~~~~

This module contains all exceptions.
"""


class PoolClosed(Exception):
    def __init__(self):
        super.__init__("pool closed")
