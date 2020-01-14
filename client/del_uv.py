import redis
import time
date_time = time.strftime("%Y/%m/%d")

"""
由于总量用户的不准确性，删除重新计算
"""
pool16380 = redis.ConnectionPool(host="10.0.3.40", port=16380, password="123456789",
                                 decode_responses=True)  # host是redis主机，需要redis服务端和客户端都起着 redis默认端口是6379
r16380 = redis.Redis(connection_pool=pool16380)

pool16379 = redis.ConnectionPool(host="10.0.3.40", port=16379, password="123456789",
                                 decode_responses=True)  # host是redis主机，需要redis服务端和客户端都起着 redis默认端口是6379
r16379 = redis.Redis(connection_pool=pool16379)

#总用户
r16380.delete("ALL_UV")
key_list = r16380.keys("*_UV")
r16380.delete(*key_list)


key_list = r16379.keys("*_UV")
for key in key_list:
    num = r16379.scard(key)
    r16380.set(key,num)
    r16380.incrby("ALL_UV",num)

#当天新增用户
r16380.delete("NUV_"+date_time)
key_list = r16380.keys("*_NUV_" + date_time)
r16380.delete(*key_list)

key_list = r16379.keys("*_NUV_" + date_time)
for key in key_list:
    num = r16379.scard(key)
    r16380.set(key,num)
    r16380.incrby("NUV_"+date_time,num)

#当天活跃用户

r16380.delete("DAU_"+date_time)
key_list = r16380.keys("*_DAU_" + date_time)
r16380.delete(*key_list)

key_list = r16379.keys("*_DAU_" + date_time)
for key in key_list:
    num = r16379.scard(key)
    r16380.set(key,num)
    r16380.incrby("DAU_"+date_time,num)
