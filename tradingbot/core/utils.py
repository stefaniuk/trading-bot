# -*- coding: utf-8 -*-

"""
tradingbot.core.utils
~~~~~~~~~~~~~~

This module provides utility functions that are used within tradinbot.
"""

import time
# import functools - for memoize
from threading import Thread, active_count
from .exceptions import PoolClosed

# logging
import logging
logger = logging.getLogger('tradingbot.utils')


def launch_thread(th, name):
    if not isinstance(th, Thread):
        raise ValueError("thread not given")
    th.daemon = True
    th.start()
    logger.debug("Thread #%d launched - %s launched" %
                 (active_count(), name))


# -~- Command Pool -~-
class CommandPool(object):
    def __init__(self):
        self.pool = []
        self.results = []
        self.working = False
        self.open = True

    def check_add(self, command, args=[], kwargs={}):
        cmd = [command, args, kwargs]
        if cmd not in self.pool:
            self.add(command, args, kwargs)

    def add(self, command, args=[], kwargs={}):
        if not self.open:
            logger.warning("pool closed")
            raise PoolClosed()
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

    def wait_finish(self, command, args=[], kwargs={}, timeout=60):
        """add and wait to finish"""
        self.add(command, args, kwargs)
        timeout = time.time() + timeout
        while [command, args, kwargs] in self.pool:
            time.sleep(1)
            if time.time() > timeout:
                raise TimeoutError("%s not finished" % str(command.__name__))
        res = [x for x in self.results if [command, args, kwargs] in x]
        if res:
            if isinstance(res[0][1], Exception):
                raise res[0][1]

    def wait_result(self, command, args=[], kwargs={}, timeout=30):
        """wait until result has been given"""
        self.add(command, args, kwargs)
        return self.wait(command, args, kwargs, timeout)

    def wait_single_result(self, command, args=[], kwargs={}, timeout=30):
        """check if single and wait until result has been given"""
        self.check_add(command, args, kwargs)
        return self.wait(command, args, kwargs, timeout)

    def work(self):
        """work for every command in pool"""
        self.working = True
        for func in self.pool:
            try:
                res = func[0](*func[1], **func[2])
            except Exception as e:
                res = e
            if res is not None:
                self.results.append((func, res))
        self.pool.clear()
        self.working = False

    def get(self, command, args=[], kwargs={}):
        """get result"""
        f = [command, args, kwargs]
        try:
            res = [x for x in self.results if x[0] == f][0]
            self.results.remove(res)
            return res[1]
        except Exception:
            raise

    def block(self):
        """block pool"""
        self.open = False
        logger.debug("closing pool")

    def close(self):
        """close pool"""
        self.block()
        timeout = time.time() + 10
        while time.time() < timeout:
            if self.working:
                time.sleep(1)
            else:
                break
        if not self.working:
            logger.warning("pool not closed")
