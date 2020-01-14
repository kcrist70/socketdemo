import selectors
import socketserver
import sys
import socket
sys.path.append("..")
from module.myserver import MyServer


_ServerSelector = selectors.DefaultSelector

socket.setdefaulttimeout(10)

class ThreadingTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


if __name__ == '__main__':
    s = ThreadingTCPServer(('10.0.4.126', 8585), MyServer)
    s.serve_forever()