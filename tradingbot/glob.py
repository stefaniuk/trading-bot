# -*- coding: utf-8 -*-

"""
tradingbot.glob
~~~~~~~~~~~~~~

This module provides the globals.
"""

import os.path
from .events import BotEvent
from .patterns import Singleton
from .configurer import Configurer, Collector

# logging
import logging
logger = logging.getLogger('tradingbot.globals')

file_path = {
    'main': os.path.join(os.path.dirname(__file__), "data.yml"),
    'strategy': os.path.join(os.path.dirname(__file__), "core",
                             "strategies"),
}


class Glob(Collector, metaclass=Singleton):
    def __init__(self):
        self.collection = {'root': {'preferences': []}}
        self.events = {}  # init events
        event_list = ['REC_LIVE', 'POS_LIVE', 'HANDLEPOS_LIVE']
        for x in event_list:
            self.events[x] = BotEvent()
        self.conf_new('main')
        logger.debug("initiated observables")
        logger.debug("initiated observer")

    def conf_new(self, name, path=None):
        """configure new configurer"""
        conf_name = (name + 'Conf')
        logger.debug("initiated %s" % conf_name)
        if path is None:
            conf = Configurer(file_path[name], name)
        else:
            conf = Configurer(path, name)
        setattr(self, conf_name, conf)
        configured = getattr(self, conf_name)
        configured.attach(self)
        configured.read()

    def init_strategy(self, name):
        """init strategy configurer (lazy evaluation)"""
        path = os.path.join(file_path['strategy'], name + '.yml')
        if not os.path.isfile(path):
            logger.error("strategy not found")
            raise FileNotFoundError("file not found in strategy folder")
        self.conf_new(name, path)
        return getattr(self, name + 'Conf')
