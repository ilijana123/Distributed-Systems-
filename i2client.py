
# 2. Да се направи социјална мрежа за потребите на една детска градинка во која работат 
# воспитувачи, готвачи и административци. Програмата да биде дистрибуирана P2P клиент 
# сервер апликација со употреба на TCP и RPC. Клиентот треба да се регистрира на сервер со 
# единствено корисничко име, лозинка и позиција. Доколку позицијата му е воспитувач, се 
# чува и дополнителна информација за тоа на која група е воспитувач, а доколку е готвач се 
# чува дополнителна информација за што е специјализиран. По успешна регистрација клиентот
# треба да се најави на серверот. Најавените клиенти можат да праќаат пораки до било кој од 
# другите најавени клиенти. Градинката функционира така што секој административец може да
# креира група со името од “дополнителната информација”, а потоа тука може да се приклучат 
# готвачите и воспитувачите и да испраќаат пораки, но доколку групата им е соодветна 
# (дополнителната информација се совпаѓа со името на групата). Исто така има и група во која 
# членуваат сите административци (неа може да ја креира било кој административец, но само 
# еднаш, а притоа групата ќе има име administracija) и тука исто така секој од 
# административците кој се приклучил може да испраќа пораки. Секој вработен има можност и
# да се одјави од серверот.
# Доколку готвач или воспитувач се обиде да се приклучи во групата на административците 
# или некој вработен се обиде да се приклучи во несоодветна група да му се даде информација 
# дека не може и поради која причина.
# Притоа, регистрацијата, најавата, одјавата, креирањето на група се контролна комуникација
# со северот, додека праќањето на порака од клиент до друг клиент или група е податочна
# комуникација. (60п)
import xmlrpc.client as client
from socket import *
import threading, struct

def recv_all(sock, length):
    data = b''
    while len(data) < length:
        more = sock.recv(length-len(data))
        if not more:
            raise EOFError(f'socket closed with {len(data)} bytes into a {length}-byte message')
        data += more
    return data

s = socket(AF_INET,SOCK_STREAM)

def opsluzi(s):
    s.listen(2)
    while True:
        sc, sockname = s.accept()
        dolz = struct.unpack("!i",recv_all(sc,4))[0]
        data = recv_all(sc, dolz)
        data = data.decode()
        #split() ?
        print(data)
        sc.close()

proxy = client.ServerProxy('http://127.0.0.1:7001', allow_none=True)

while True:
    what = input('What is next? \n\t r - registracija \n\t n - najava \n\t o - odjava \n\t k - kreiraj_grupa'
    ' \n\t pp - prikluchi_grupa \n\t nn - napushti_grupa \n\t ik - isprati_do_korisnik '
    '\n\t ig - isprati_do_grupa \n Your choice: ')

    if what == 'r':
        korime = input('Vnesi korisnicko ime')
        lozinka = input('Vnesi lozinka')
        uloga = input("Uloga (administrator/vospituvac/gotvac): ")

        dop_info = ""
        if uloga == "vospituvac":
            dop_info = input("Vo koja grupa rabotiš (grupaA, grupaB...)? ")
        elif uloga == "gotvac":
            dop_info = input("Za što si specializiran (riba, meso...)? ")
        print(proxy.registracija(korime, lozinka, uloga))
    
    if what == 'n':
        korime = input('Vnesi korisnicko ime')
        lozinka = input('Vnesi lozinka')
        s.bind(('localhost', 0))
        print(s.getsockname())
        threading.Thread(target=opsluzi, args=(s,)).start()
        print(proxy.najava(korime, lozinka, s.getsockname()[0], s.getsockname()[1]))

    if what == 'o':
        print(proxy.odjava(korime))

    if what == 'k':
        ime = input('Vnesi ime na novata grupa ')
        print(proxy.kreiraj_grupa(ime,korime))
    
    if what == 'pp':
        ime_grupa = input('Vo koja grupa? ')
        print(proxy.prikluci_grupa(ime_grupa, korime)) # s.getsockname()[0]....
    
    if what == 'nn':
        ime_grupa = input('Od koja grupa sakate da izlezete? ')
        print(proxy.napusti_grupa(ime_grupa, korime))

    if what == 'ik':
        dokogo = input('Do kogo sakate da ispratite poraka? ')
        result = proxy.isprati_korisnik(dokogo, korime)

        if isinstance(result, list):
            addr, port = result
            sp = socket(AF_INET, SOCK_STREAM)
            sp.connect((addr, port))
            poraka = input('Vnesi poraka: ')
            poraka = korime + ": " + poraka
            dolz = len(poraka)
            sp.sendall(struct.pack("!i",dolz)+poraka.encode())
            sp.close()

        else:
            print(result)
    
    if what == 'ig':
        dokoja = input('Do koja grupa? ')
        clenovi = proxy.isprati_grupa(dokoja, korime)

        poraka = input('Vnesi poraka do grupa: ')
        poraka = dokoja + ': '+ poraka
        dolz = len(poraka)
        if isinstance(clenovi, dict):
            for clen in clenovi:
                addr, port = clenovi[clen]
                if addr == s.getsockname()[0] & port == s.getsockname()[1]:
                    continue
                sp = socket(AF_INET,SOCK_STREAM)
                sp.connect(addr,port)
                sp.sendall(struct.pack("!i",dolz)+poraka.encode())
                sp.close()
        else:
            print(clenovi)
    

