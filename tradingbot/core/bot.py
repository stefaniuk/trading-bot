from tradingAPI import API
from getpass import getpass

from .color import *
from .config import Configurer

class Bot(object):
    def __init__(self):
        self.api = API
        self.config = Configurer("data.ini")

    def conf(self):
        print(bold(blue("------ CONFIG ------")))
        print("Add your credentials")
        print("for Trading212")
        print(bold(blue("--------------------")))
        username = input(bold(yellow("Username: ")))
        password = getpass(bold(yellow("Password: ")))
        self.config.addLogin(username, password)

    def checkConf(self):
        if not self.config.checkFile():
            self.conf()
        else:
            self.config.read()