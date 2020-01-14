import os
import logging
from logging.handlers import TimedRotatingFileHandler
import redis
import sys


def logger():
    if not os.path.exists('../log'):
        os.mkdir('../log/')
    logger = logging.getLogger('socket_log')
    logger.setLevel(level=logging.INFO)
    filehandler = TimedRotatingFileHandler('../log/server.log', "D", 1, 10)
    filehandler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    filehandler.setFormatter(formatter)
    logger.addHandler(filehandler)
    return logger



def redis_web():
    pool16380 = redis.ConnectionPool(host="10.0.3.40", port=16380, password="123456789",
                                decode_responses=True)
    r16380 = redis.Redis(connection_pool=pool16380)
    return r16380


def redis_set():
    pool16379 = redis.ConnectionPool(host="10.0.3.40", port=16379, password="123456789",
                                decode_responses=True)
    r16379 = redis.Redis(connection_pool=pool16379)
    return r16379


logger = logger()
try:
    res = redis_web().ping()
    if not res:
        logger.error("redis_web not connnect")
        sys.exit(1)
except:
    logger.error("except redis_web not connect")
    sys.exit(1)

try:
    res = redis_set().ping()
    # print(res)
    if not res:
        logger.error("redis_set not connnect")
        sys.exit(1)
except:
    logger.error("except redis_set not connect")
    sys.exit(1)

