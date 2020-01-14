import socketserver
import os, hmac
import struct
from conf import settings
import time

secret_key = b'phone log transfer'
logger = settings.logger
all_ids_dict = dict()
log_date = dict()


class MyServer(socketserver.BaseRequestHandler):

    def handle(self):
        logger.info("new client connection: %s:%s" % self.client_address)
        if not self.conn_auth:
            logger.error("%s:%s illegal connect" % self.client_address)
            self.request.close()
            return

        while True:
            try:
                length_data = self.request.recv(4)
                if not length_data:
                    logger.error("client is close: %s" % self.request)
                    self.request.close()
                    break
                if len(length_data) != 4:
                    self.request.close()
                    logger.error("head data is illegal: %s" % length_data)
                    break
                length = struct.unpack('i', length_data)
                data = self.request.recv(length[0])
                if len(data) != length[0]:
                    logger.error("received data is not enough for length %s : %s" % (length[0], data))
                    self.request.close()
                    break
                data_list = data.decode("utf-8").split("\t")
                logger.debug(data_list)
                if len(data_list) != 3:
                    logger.error("recv body data is illegal: %s" % data)
                    self.request.close()
                    break
                self.handle_data(data_list)
            except Exception as e:
                logger.error(e)
                self.request.close()
                break

    def handle_data(self, data):
        global all_ids_dict
        global log_date
        if not log_date.get(data[1]):
            log_date[data[1]] = data[0]
            logger.info("now date of log_date[%s] is: %s" %(data[1],data[0]))
        if len(data[0].split("/")) == 3:
            if log_date[data[1]] != data[0]:
                all_ids_dict[data[1]] = set()
                log_date[data[1]] = data[0]
                logger.info("reset log_date[%s]: %s" %(data[1],data[0]))
                logger.info("reset all_ids_dict[%s] to empty" %data[1])
        else:
            logger.error("date is not correct form： %s" %data[0])
        if not all_ids_dict.get(data[1]):
            all_ids_dict[data[1]] = set()
            logger.info("create all_ids_dict[%s]" %data[1])
        if data[2] not in all_ids_dict[data[1]]:
            all_ids_dict[data[1]].add(data[2])
            logger.debug(all_ids_dict)
            # 共用
            # 当天新增单个uv，当天新增单个uv集合
            nuv_appid_name = data[1] + "_NUV_" + data[0]
            # 当天活跃单个UV, 当天活跃用户集合
            dau_appid_name = data[1] + "_DAU_" + data[0]
            # 全部注册用户,历史注册集合
            all_name = "ALL_UV"
            # 单个注册用户,用户注册集合
            appid_name = data[1] + "_UV"
            # 只记录数值
            # 当天新增全部uv
            nuv_all_name = "NUV_" + data[0]
            # 当天活跃全部uv
            dau_all_name = "DAU_" + data[0]
            r_set = self.redis_set
            r_web = self.redis_web
            # 添加用户至活跃集合，并根据返回值判定活跃用户在没在集合
            dau_status = r_set.sadd(dau_appid_name, data[2])
            logger.debug("%s %s dau status: %s"%(dau_appid_name,data[2],dau_status))
            # 不在集合时
            if dau_status:
                # 增量计数器当天单个活跃用户，增量当天全部用户
                logger.debug("%s is not in %s"%(data[2],dau_appid_name))
                with r_web.pipeline(transaction=False) as p:
                    p.incr(dau_appid_name).incr(dau_all_name)
                    p.execute()
                nuv_status = r_set.sadd(appid_name, data[2])
                logger.debug("nuv_status: ", nuv_status)
                if nuv_status:
                    r_set.sadd(nuv_appid_name, data[2])
                    with r_web.pipeline(transaction=False) as p:
                        p.incr(nuv_appid_name).incr(nuv_all_name).incr(all_name).incr(appid_name)
                        p.execute()
                    logger.info("%s new %s" % (data[2], appid_name))

    @property
    def redis_set(self):
        while True:
            redis_conn = settings.redis_set()
            try:
                res = redis_conn.ping()
                if res:
                    break
            except:
                logger.error("can not connect redis set")
                time.sleep(1)
        return redis_conn

    @property
    def redis_web(self):
        while True:
            redis_conn = settings.redis_web()
            try:
                res = redis_conn.ping()
                if res:
                    break
            except:
                logger.error("can not connect redis web")
                time.sleep(1)
        return redis_conn

    @property
    def conn_auth(self):
        logger.info("auth the connect legal %s:%s" % self.client_address)
        msg = os.urandom(32)
        try:
            self.request.sendall(msg)
            h = hmac.new(secret_key, msg)
            digest_str = h.digest()
            respone = self.request.recv(len(digest_str))
            logger.info("%s:%s connect success"% self.client_address)
            if hmac.compare_digest(respone, digest_str):
                self.request.sendall(bytes("1",encoding="utf-8"))
            else:
                return False
        except Exception as e:
            logger.error(e)
            return False
        return True
