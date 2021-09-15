import socket

HOST = "127.0.0.1"        # The remote host
PORT = 8080               # The same port as used by the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(bytes(input().encode("utf-8")))