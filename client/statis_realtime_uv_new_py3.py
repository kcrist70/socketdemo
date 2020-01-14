# coding: utf8
# !/usr/bin/env python
import pika
import sys
import argparse
import time
import hmac, os
from multiprocessing import Queue, Process
import socket
import struct

# 所有UV前缀 ALL_UV
# 当天新增UV NUV_
# 当天活跃UV DAU_
secret_key = b'phone log transfer'
parser = argparse.ArgumentParser()
parser.add_argument("-rb_h", "--rabbitmq_host", help="the host of rabbitmq", default="172.16.0.208", type=str)
parser.add_argument("-rb_p", "--rabbitmq_port", help="the port of rabbitmq", default=5672, type=int)
parser.add_argument("-rb_u", "--rabbitmq_user", help="the user of rabbitmq", default="admin", type=str)
parser.add_argument("-rb_pwd", "--rabbitmq_password", help="the password of rabbitmq", default="123456789", type=str)
parser.add_argument("-rb_keys", "--rabbitmq_binding_keys", help="the binding keys of rabbitmq", default="#", type=str)
args = parser.parse_args()
connection = pika.BlockingConnection(pika.ConnectionParameters(host=args.rabbitmq_host, port=args.rabbitmq_port,
                                                               credentials=pika.PlainCredentials(args.rabbitmq_user,
                                                                                                 args.rabbitmq_password)))
channel = connection.channel()
channel.exchange_declare(exchange='amq.topic', exchange_type='topic', durable=True)
body_q = Queue()
try:
    result = channel.queue_declare("phonelog", durable=True)
except Exception:
    channel = connection.channel()
    result = channel.queue_declare("phonelog", durable=True)
queue_name = result.method.queue
binding_keys = args.rabbitmq_binding_keys
if not binding_keys:
    sys.stderr.write("Usage: %s [binding_key]...\n" % sys.argv[0])
    sys.exit(1)
print(queue_name)
print(binding_keys)
for binding_key in binding_keys:
    channel.queue_bind(exchange='amq.topic', queue=queue_name, routing_key=binding_key)
all_device_ids = dict()
print(' [*] Waiting for logs. To exit press CTRL+C')
log_date = ""
socket.setdefaulttimeout(1)

try:
    ip_port = ('123.58.20.71', 8585)
    conn_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn_server.connect(ip_port)
    msg = conn_server.recv(32)
    h = hmac.new(secret_key, msg)
    digest_str = h.digest()
    conn_server.sendall(digest_str)
    if str(conn_server.recv(1), encoding="utf-8") != "1":
        sys.exit(1)
    conn_server.close()
except Exception as er:
    print(er)
    sys.exit(1)


def conn_auth():
    while True:
        try:
            ip_port = ('123.58.20.71', 8585)
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(ip_port)
            msg = client.recv(32)
            h = hmac.new(secret_key, msg)
            digest_str = h.digest()
            client.sendall(digest_str)
            if str(client.recv(1), encoding="utf-8") == "1":
                break
        except Exception as err:
            print(err)
            time.sleep(0.1)
    return client


tcp_client = None


def callback(ch, method, properties, body):
    # print(" [x] %r:%r" % (method.routing_key, body))
    # print("%s" % (body))
    # global key_num
    global all_device_ids
    global log_date
    global args
    global body_q
    # print(ch,method,properties,body)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    body_q.put(body)


def producer(name, q):
    global queue_name
    global channel
    channel.basic_consume(on_message_callback=callback, queue=queue_name, auto_ack=False)
    channel.start_consuming()


def treater(name, q):
    global args
    global log_date
    global all_device_ids
    global tcp_client
    if tcp_client is None:
        tcp_client = conn_auth()
    while True:
        body = body_q.get().decode("utf-8")
        # print(body)
        if log_date == "":
            items = body.split(" [ERROR] ")
            if len(items) < 2:
                items = body.split(" [INFO ] ")
            if len(items) >= 2:
                next_items = items[0].split(" ")
                if len(next_items):
                    log_date = next_items[0]
        if log_date != "":
            current_date = body.split(" ", 1)[0]
            if len(current_date.split("/")) == 3:
                if log_date != current_date:
                    all_device_ids = dict()
                    log_date = current_date
        if "Segment Request:" in body or "Nlp Request:" in body or "Resource Request:" in body and '"deviceId":"' in body and '"appId":"' in body:
            # print body
            if '"deviceId":"' in body and '"appId":"' in body:
                items = body.split('"deviceId":"')[1].split('","')
                id_items = body.split('"appId":"')[1].split('","')
                if len(items) > 1:
                    device_id = items[0]
                    if len(id_items) > 1:
                        appid = id_items[0]
                        # print(device_id)
                        if device_id is not None and device_id != "":
                            # if not all_device_ids.has_key(device_id):
                            if not all_device_ids.get(appid):
                                all_device_ids[appid] = set()
                                all_device_ids[appid].add(device_id)
                                # all_device_ids[device_id]=1
                                data = bytes(log_date + "\t" + str(appid) + "\t" + device_id, encoding="utf-8")
                                try:
                                    tcp_client.sendall(struct.pack("i", len(data)) + data)
                                except socket.error:
                                    tcp_client = conn_auth()
                                    tcp_client.sendall(struct.pack("i", len(data)) + data)
                            elif device_id not in all_device_ids.get(appid):
                                all_device_ids[appid].add(device_id)
                                data = bytes(log_date + "\t" + str(appid) + "\t" + device_id, encoding="utf-8")
                                try:
                                    tcp_client.sendall(struct.pack("i", len(data)) + data)
                                except socket.error:
                                    tcp_client = conn_auth()
                                    tcp_client.sendall(struct.pack("i", len(data)) + data)
                            else:
                                pass


if __name__ == '__main__':
    p1 = Process(target=producer, args=('producer', body_q))
    c1 = Process(target=treater, args=("consume", body_q))
    p1.daemon = True
    p1.start()
    c1.start()
    c1.join()
