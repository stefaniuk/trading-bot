# -*- coding: utf-8 -*-

"""
tradingbot.patterns
~~~~~~~~~~~~~~

This module provides design patterns.
"""


# ~ OBSERVER PATTERN ~
class Observable(object):
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def notify_observers(self, *args, **kwargs):
        for observer in self._observers:
            observer.notify(self, *args, **kwargs)


class Observer(object):
    def __init__(self, observable=None):
        if observable is not None:
            self.register_obs(observable)

    def register_obs(self, observable):
        if self not in observable._observers:
            observable.attach(self)

    def notify(self, observable, *args, **kwargs):
        """catch the event"""
        raise NotImplementedError("Need to implement to catch events")


# ~ SINGLETON ~
class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(
                *args, **kwargs)
        return cls._instances[cls]
