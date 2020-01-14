import socket
import time
conn = None
# socket.setdefaulttimeout(20)
st = time.time()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ip_port=("127.0.0.1",8080)
s.settimeout(10)
s.bind(ip_port)
s.listen(4)
try:

    conn,addr = s.accept()
    if conn:
        print(conn)
    print(time.time() - st)
except Exception as e:
    print(time.time() - st)
    raise e
try:
    s = conn.recv(4096)
    print(s)
    print(time.time() - st)
except Exception as e:
    print(time.time() - st)
    print(e)