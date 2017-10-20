from ..algorithm import BaseAlgorithm

# logging
import logging
logger = logging.getLogger('tradingbot.algo.Ross123')


class Ross123(BaseAlgorithm):
    def __init__(self):
        super().__init__()
        logger.debug("Ross123 algorithm initiated")
