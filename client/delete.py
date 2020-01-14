import redis
import time
import datetime


pool16379 = redis.ConnectionPool(host="10.0.3.40", port=16379, password="123456789",
                                 decode_responses=True)
r16379 = redis.Redis(connection_pool=pool16379)



date_time = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y/%m/%d")
key_list = r16379.keys("*_" + date_time)
r16379.delete(*key_list)