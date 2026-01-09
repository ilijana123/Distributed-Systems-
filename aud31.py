# Да се напише програма во која клиентите праќаат порака до серверот со која се
# регистрираат. Откако ќе се регистрираат, клиентите можат да праќаат пораки до друг
# клиент. Истовремено при праќање на порака, клиентите може да примаат пораки од страна
# на други клиенти. Препраќањето на пораките го врши серверот.

import socket, sys, threading

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # udp 
MAX = 65535
PORT = 7777

class klient():
    def __init__(self, ime, lozinka, adresa):
        self.ime = ime
        self.lozinka = lozinka
        self.adresa = adresa

        self.razgovori = {}
    
    def dodajPoraka(self, poraka, korisnik):
        if korisnik in self.razgovori:
            self.razgovori[korisnik] += [poraka]
        else:
            self.razgovori[korisnik] = []
            self.razgovori[korisnik] = [poraka]

def klientPrimaj(s):
    while True:
        data,addr = s.recvfrom(MAX)
        print(data.decode())

if sys.argv[1] == 'server':
    klienti = {}
    s.bind(('127.0.0.1',PORT))
    print('Server up and listening')

    while True:
        data, addr = s.recvfrom(MAX)
        msg = data.decode().split('|') # data = b'registracija|$ime|$lozinka' / b'porakado|korime|poraka'

        if msg[0] == 'registracija':
            ime = msg[1]
            if ime in klienti:
                print('Veke posoti vakov zapis!')
                s.sendto(('Korisnickoto ime veke posoti, izberete drugo!').encode(),addr)
            else:
                lozinka = msg[2]
                korisnik = klient(ime, lozinka, addr)
                klienti[ime] = korisnik
                print('Se registrira ', ime)
                s.sendto(('Uspesna registracija').encode(),addr)

        elif msg[0] == 'porakado':
            korime = msg[1]
            if korime in klienti:
                poraka = msg[2]
                for korisnik in klienti.values():
                    if korisnik.adresa == addr:
                        odkogo = korisnik.ime
                        break
                print('Se ispraka poraka \''+poraka+'\'\n')
                tosend = odkogo +': '+ poraka
                s.sendto(tosend.encode(), klienti[korime].adresa)

                klienti[korime].dodajPoraka(tosend, odkogo)
                klienti[odkogo].dodajPoraka(tosend, korime)
            else:
                s.sendto((korime + ' ne e  registriran korisnik na server!').encode(), addr)
        
        elif msg[0] == 'prikazi_poraki':
                ime = msg[1]
                if ime in klienti:
                    history = klienti[ime].razgovori
                    response = "\n".join([f"{sender}: {', '.join(msgs)}" for sender, msgs in history.items()])
                    if response:
                        s.sendto(response.encode(),klienti[ime].adresa)
                    else:
                        s.sendto(('Nemate poraki!').encode(), klienti[ime].adresa)

elif sys.argv[1] == 'client':
    while True:
        ime = input('Vnesete korisnicko ime (unikatno)')
        lozinka = input('Vnesete lozinka')
        s.sendto(('registracija|'+ime+'|'+lozinka).encode(),('127.0.0.1',PORT))

        response, _ = s.recvfrom(MAX)
        response = response.decode()
        if response == 'Korisnickoto ime veke posoti, izberete drugo!':
            print(response)
        else:
            print(response)
            break
    
    threading.Thread(target=klientPrimaj, args=(s,)).start()

    while True:
        sto = input('poraka ili vrati_poraki')
        if sto == 'poraka':
            dokogo = input('Do kogo?')
            poraka = input('Poraka: ')
            s.sendto(('porakado|'+dokogo+'|'+poraka).encode(),('127.0.0.1',PORT))
        elif sto == 'vrati_poraki':
            vrati = 'prikazi_poraki|'+ime
            s.sendto(vrati.encode(),('127.0.0.1',PORT))
else:
    print(SystemError, 'Gresno povikana programa!')

