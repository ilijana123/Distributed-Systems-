import sys,socket

MAX = 65535
PORT = 7777

s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if sys.argv[-1] == 'server': #posleden argument
    s.bind(('127.0.0.1', PORT))
    print(f'Server up and listening at {s.getsockname()}')

    while True:
        data,addr = s.recvfrom(MAX)
        msg = data.decode()
        print(f'Client at {addr} says {msg}')
        s.sendto((f'Your msg was {len(msg)}').encode(), addr)

elif sys.argv[-1] == 'client':
    #print(f'Address before sending {s.getsockname()}\n')
    msg = input('Enter text:\n')
    s.sendto(msg.encode(), ('127.0.0.1',PORT))
    print(f'Address after sending: {s.getsockname()}\n')
    data, _ = s.recvfrom(MAX)
    print(f'\nServer says {data.decode()}')

else:
    print(f'Upatstvo: python {sys.argv[0]} server/client')
    sys.exit(-1)
