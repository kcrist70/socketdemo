import socket
import hmac
import struct
import time


secret_key = b'phone log transfer'

def conn_auth(conn):
    msg=conn.recv(32)
    h = hmac.new(secret_key,msg)
    digest_str = h.digest()
    conn.sendall(digest_str)


ip_port=('127.0.0.1',8088)
buffer_size = 1024
tcp_client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
tcp_client.connect(ip_port)
conn_auth(tcp_client)
count = 0
while True:
    # a= tcp_client.recv(1024)
    # print(a)
    try:
        print(tcp_client)
        print(111111111111)
        msg = bytes('2019/05/09\t10018\tlGob2j1XHjuihgsrmlUbuQ==',encoding="utf-8")
        tcp_client.sendall(struct.pack("i", len(msg))+msg)
        # if not msg:continue
        # if msg == 'quit':break
        # tcp_client.sendall(msg.encode('utf-8'))
        # data = tcp_client.recv(buffer_size)
        # print(data.decode('utf-8'))
        time.sleep(1)
        if count == 10:
            break
        else:
            count += 1
    except socket.error:
        tcp_client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        tcp_client.connect(ip_port)
        conn_auth(tcp_client)


tcp_client.close()
