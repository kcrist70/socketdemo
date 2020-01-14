import redis
pool16379 = redis.ConnectionPool(host="10.0.3.40", port=16379, password="123456789",
                            decode_responses=True)
r16379 = redis.Redis(connection_pool=pool16379)


with open("/root/all_user_2018-04-12_2019-05-09") as f:
    for i in f:
        li = i.strip().split("\t")
        if len(li) != 4:
            continue
        if li[3] == "true":
            continue
        r16379.sadd(li[0] + "_UV",li[1])