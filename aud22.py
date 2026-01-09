import sys, socket, random

MAX = 65535

s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if sys.argv[-1] == 'server':
    s.bind(('localhost',8765))
    print("Server up and listening\n")

    while True:
        data, addr = s.recvfrom(MAX)
        if random.randint(0,1):
            msg = data.decode()
            print(f'Client says {msg}')
            s.sendto(('Your transfer was successful').encode(),addr)
        else:
            print('Pretending to drop packet...')

if sys.argv[-1] == 'client':
    msg = input('Enter msg:\n')
    delay = 0.5
    while True:
        s.sendto(msg.encode(),('127.0.0.1',8765))
        print(f'Waiting up to {delay} seconds for the server to reply\n')
        s.settimeout(delay)
        try:
            data = s.recvfrom(MAX)
        except socket.timeout:
            delay *= 2
            if delay > 2.0:
                raise RuntimeError('I think the server is down...')
        except:
            raise
        else:
            break
    print('The server says',repr(data))

else:
    print('Greska pri povikuvanje\n')
    sys.exit(-1)