from tradingAPI import API
from getpass import getpass

from .color import *
from .config import Configurer
from .algorithm import *

class Bot(object):
    def __init__(self):
        self.api = API()
        self.config = Configurer("data.ini")
        
    def conf(self):
        if not self.config.checkFile():
            print(info.header("config"))
            print("Add your credentials")
            print("for Trading212")
            print(bold(blue("--------------------")))
            username = input(info.user_input("Username: "))
            password = getpass(info.user_input("Password: "))
            print(bold(blue("--------------------")))
            print("Add your information")
            print("for a monitoring")
            print("account")
            print(bold(blue("--------------------")))
            username2 = input(info.user_input("Username: "))
            password2 = getpass(info.user_input("Password: "))
            stocks = input(info.user_input("Favourite stocks (sep by spaces): ")).split(' ')
            self.config.addLogin(username, password)
            self.config.addMonitor(username2, password2, stocks)
        else:
            self.config.read()

    def start(self):
        self.pivot = Pivot(self.api, self.config)
        self.pivot.start()

    def stop(self):
        self.pivot.stop()