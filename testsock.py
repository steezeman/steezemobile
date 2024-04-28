import socket

host = "192.168.88.210"
port = 2424                   # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
s.sendall(b'Hello, world')
data = s.recv(2)
s.close()
print('Received', repr(data))
