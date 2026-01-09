from socket import *
import sys, threading, struct

s = socket(AF_INET, SOCK_STREAM) #tcp socket
s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)

PORT = 6789

def recv_all(sock, length):
    data = b''
    while len(data) < length:
        more = sock.recv(length-len(data))
        if not more:
            raise EOFError(f'socket closed with {len(data)} bytes into a {length}-byte message')
        data += more
    return data

# poraka = '$length $data' / '6Zdravo' -10bytes
# b'reg|korime...' / b'poraka|korime|data...'

def citaj(s):
    while True:
        length = struct.unpack("!i", recv_all(s,4))[0]
        data = recv_all(s,length)
        data = data.decode().split('|')
        print(data[0] + data[1] + '\n')

s.connect(('localhost',PORT)) # (2)

uname = input('Vnesi korisnicko ime (unikatno):\n')
msg = 'reg|' + uname
length = len(msg)
fullmsg = struct.pack("!i", length) + msg.encode()
s.sendall(fullmsg)

#otpakuvaj prvi 4 bajti od porakata - za dolzinata
length = struct.unpack("!i", recv_all(s,4))[0] # unpack vraka tuple duri i za eden argument
reply = recv_all(s,length).decode()

if reply == 'nedozvoleno':
    print('Korisnickoto ime e veke zafateno!')
    sys.exit(-1)
elif reply == 'registered':
    print(f"Uspesna registracija so korisnicko ime {uname}")
    try:
        threading.Thread(target=citaj, args=(s,)).start()
        while True:
            dokogo = input('Do kogo?\n')
            poraka = input('poraka:\n')

            msg = 'poraka|'+dokogo+'|'+poraka
            length = len(msg)
            fullmsg = struct.pack("!i",length) + msg.encode()
            s.sendall(fullmsg)
    except:
        print('Greska')
        sys.exit(-1)