import socket
import time
import hmac
socket.setdefaulttimeout(20)
st = time.time()
secret_key = b'phone log transfer'
ip_port=("127.0.0.1",8585)
# s.settimeout(15)
while True:
    try:
        print("start")
        ip_port = ('127.0.0.1', 8585)
        tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_client.connect(ip_port)
        msg = tcp_client.recv(32)
        h = hmac.new(secret_key, msg)
        digest_str = h.digest()
        tcp_client.sendall(digest_str)
        if str(tcp_client.recv(1), encoding="utf-8") == "1":
            print("connect ok")
            break
        else:
            tcp_client.close()
    except Exception as e:
        print(time.time() - st)
        print(e)
time.sleep(20)
