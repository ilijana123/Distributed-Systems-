import xmlrpc.client as client
from socket import *
import threading,struct

def recv_all(sock, length):
    data = b''
    while len(data) < length:
        more = sock.recv(length-len(data))
        if not more:
            raise EOFError(f'socket closed with {len(data)} bytes into a {length}-byte message')
        data += more
    return data

s=socket(AF_INET,SOCK_STREAM)

def opsluzi(s):
    s.listen(2)
    while True:
        sc,sockname=s.accept()
        dolz=struct.unpack("!i",recv_all(sc,4)[0])
        data=recv_all(sc,dolz)
        data=data.decode()
        print(data)
        sc.close()

proxy = client.ServerProxy('http://127.0.0.1:PORT',allow_none=true)

while True:
    what = input('What is next? \n\t r - registracija \n\t n - najava \n\t o - odjava \n\t k - kreiraj_grupa'
    ' \n\t pp - prikluchi_grupa \n\t nn - napushti_grupa \n\t ik - isprati_do_korisnik '
    '\n\t ig - isprati_do_grupa \n Your choice: ')

    if what == 'r':
        korime=input("Vnesi kor ime")
        lozinka=input("Vnesi lozinka: ")
        uloga=input("Vnesi uloga: ")
        print(proxy.regitracija(korime,lozinka,uloga))

    if what=='n':
        korime=input("Vnesi kor ime")
        lozinka=input("Vnesi lozinka: ")
        s.bind(('localhost',0))
        print(s.getsockname())
        threading.Thread(target=opsluzi,args=(s,)).start()
        print(proxy.najava(korime,lozinka,s.getsockname()[0],s.getsockname()[1]))

    if what=="o":
        print(proxy.odjava(korime))

    if what=="k":
        ime_grupa=input("Vnesi ima na nova grupa")
        print(proxy.kreiraj_grupa(ime))
    
    if what=="pp":
        ime_grupa=input("Vo koja grupa?")
        print(proxy.prikluci_grupa(ime_grupa,korime))
    
    if what=="nn":
        ime_grupa=input("Od koja gr sakate da izlezete?")
        print(proxy.napusti_grupa(ime_grupa,korime))

    if what=="ik":
        dokogo=input("Do kogo sakate da ja ispratite porakata")
        result=proxy.isprati_korisnik(dokogo,korime)

        if isinstance(result,list):
            addr,port=result
            sp=socket(AF_INET,SOCK_DGRAM)
            sp.connect((addr,port))
            poraka=input("Vnessete poraka: ")
            poraka=korime+":"+poraka
            dolz=len(poraka)
            sp.sendall(struct.pack("!i",dolz),poraka.encode())
            sp.close()
        else:
            print(result)
    if what=="ig":
        dokoja=input("Koja grupa: ")
        clenovi=proxy.iprati_grupa(dokoja,korime)

        poraka=input("Vnesi poraka")
        poraka=dokoja+":"+poraka
        dolz=len(poraka)
        if isinstance(clenovi,dict):
            for clen in clenovi:
                addr,port=clenovi[ime]
                if addr == s.getsockname()[0] & port==s.getsockname()[1]
                    continue
                sp=socket(AF_INET,SOCK_DGRAM)
                sp.connect((addr,port))
                sp.sendall(struct.pack("!i",dolz)+poraka.encode())
        else:
            print(clenovi)
