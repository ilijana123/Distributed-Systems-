import socket, sys, threading

s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
MAX=65535
PORT=7777

class klient():
    def __init__(self, ime, lozinka,role, adresa):
        self.ime=ime
        self.lozinka=lozinka
        self.role=role
        
        self.razgovori = {}
    
    def dodajPoraka(self, poraka, korisnik):
        if korisnik in self.razgovori:
            self.razgovori[korisnik] += [poraka]
        else:
            self.razgovori[korisnik]=[]
            self.razgovori[korisnik]=[poraka]

def klientPrimaj(s):
    while True:
        data,addr=s.recvfrom(MAX)
        print(data.decode())

while True:
    ime = input('Vnesete korisnicko ime (unikatno)')
    lozinka = input('Vnesete lozinka')
    role = input('Vnesete role (user || employee)')
    s.sendto(('registracija|'+ime+'|'+lozinka+'|'+role).encode(),('127.0.0.1',PORT))

    response, _ = s.recvfrom(MAX)
    response = response.decode()
    if response == 'Korisnickoto ime veke posoti, izberete drugo!':
         print(response)
    else:
        print(response)
        break
    
threading.Thread(target=klientPrimaj, args=(s,)).start()

while True:
    dokogo = input('Do kogo?')
    poraka = input('Poraka: ')
    s.sendto(('porakado|'+dokogo+'|'+poraka).encode(),('127.0.0.1',PORT))
else:
    print(SystemError, 'Gresno povikana programa!')