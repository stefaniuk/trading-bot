# -*- coding: utf-8 -*-

"""
tradingbot.core.utils
~~~~~~~~~~~~~~

This module provides utility functions that are used within tradinbot.
"""

import time
# import functools - for memoize
from threading import Thread

# logging
import logging
logger = logging.getLogger('tradingbot.utils')


# -~- Command Pool -~-
class CommandPool(object):
    def __init__(self):
        self.pool = []
        self.results = []
        self.working = False

    def check_add(self, command, args=[], kwargs={}):
        cmd = [command, args, kwargs]
        if cmd not in self.pool:
            self.add(command, args, kwargs)

    def add(self, command, args=[], kwargs={}):
        self.pool.append([command, args, kwargs])
        if self.working is False:
            Thread(target=self.work).start()

    def wait(self, command, args=[], kwargs={}, timeout=30):
        for _ in range(timeout):
            try:
                return self.get(command, args, kwargs)
            except Exception as e:
                exc = e
                time.sleep(1)
        raise exc

    def add_waituntil(self, command, args=[], kwargs={}, timeout=60):
        """add and wait to finish"""
        self.add(command, args, kwargs)
        timeout = time.time() + timeout
        while [command, args, kwargs] in self.pool:
            time.sleep(1)
            if time.time() > timeout:
                raise TimeoutError("%s not finished" % str(command.__name__))

    def add_and_wait_single(self, command, args=[], kwargs={}, timeout=30):
        self.check_add(command, args, kwargs)
        return self.wait(command, args, kwargs, timeout)

    def add_and_wait(self, command, args=[], kwargs={}, timeout=30):
        self.add(command, args, kwargs)
        return self.wait(command, args, kwargs, timeout)

    def work(self):
        self.working = True
        for func in self.pool:
            res = func[0](*func[1], **func[2])
            if res is not None:
                self.results.append((func, res))
        self.pool.clear()
        self.working = False

    def get(self, command, args=[], kwargs={}):
        f = [command, args, kwargs]
        try:
            res = [x for x in self.results if x[0] == f][0]
            self.results.remove(res)
            return res[1]
        except Exception:
            raise
