#  Да се напише програма во која клиенти можат да комуницираат меѓу себе со помош на
#  серверот. Клиентите се регистрираат на серверот. Откако ќе бидат регистрирани можат да
#  праќаат порака до други клиенти. Притоа, истовремено треба да можат да примаат и
#  пораки од други клиенти.

#TCP

from socket import *
import sys, threading, struct

s = socket(AF_INET, SOCK_STREAM) #tcp socket
s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)

PORT = 6789
users = dict()
l = threading.RLock()

def recv_all(sock, length):
    data = b''
    while len(data) < length:
        more = sock.recv(length-len(data))
        if not more:
            raise EOFError(f'socket closed with {len(data)} bytes into a {length}-byte message')
        data += more
    return data

def opsluziKlient(sc):
    while True:
        length = struct.unpack("!i", recv_all(sc, 4))[0]
        data = recv_all(sc, length)
        data = data.decode().split('|')
              
        if data[0] == 'reg':
            korime = data[1]
            # with l:
            l.acquire() 
            if korime in users:
                msg = 'nedozvoleno'
                length = len(msg)
                msg = struct.pack("!i",length) + msg.encode()
                sc.sendall(msg)
            else:
                users[korime] = sc
                msg = 'registered'
                length = len(msg)
                msg = struct.pack("!i",length) + msg.encode()
                sc.sendall(msg)
            l.release()
        elif data[0] == 'poraka' and data[1] in users:
            korime_dest = data[1]
            msg = korime + ':|' + data[2]
            length = len(msg)
            fullmsg = struct.pack("!i", length) + msg.encode()
            users[korime_dest].sendall(fullmsg) # socket

    # kod za registracija i preprakanje na poraki

s.bind(('localhost', PORT))
s.listen(5) # tcp connection oriented (1)
print('server up and listening..')

while True:
    sc, addr = s.accept() #(3)
    threading.Thread(target=opsluziKlient, args=(sc,)).start()
