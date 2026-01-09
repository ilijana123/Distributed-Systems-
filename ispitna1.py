# Да се напише програма која симулира UDP комуникација во која клиентите праќаат порака
# до серверот со која се регистрираат со корисничко име, лозинка и дали е вработен или 
# корисник. Откако ќе се регистрираат, клиентите можат да праќаат пораки до друг клиент.
# Пораката да не може да се прати помеѓу никој клиенти ако е поголема од 48B и тогаш
# серверот да одговори дека порака е преголема. Доколку испраќа корисник на вработен може 
# да биде до 24B, доколку пак испраќа корисник до корисник може да биде максимум 16B, а 
# доколку испраќа вработен до вработен може да биде и до 26B. Доколку пораката не е во 
# големина од дозволените граници за конкретната меѓуклиентска комуникација, а е помала од 
# 48B, серверот да врати за колку бити е надмината границата, а тоа клиентот да го испечати.
# Истовремено при праќање на порака, клиентите може да примаат пораки од страна на други
# клиенти. Препраќањето на пораките го врши серверот. (40п)

import socket, sys, threading

s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
MAX=65535
PORT=7777

class klient():
    def __init__(self, ime, lozinka,role, adresa):
        self.ime=ime
        self.lozinka=lozinka
        self.role=role
        self.adresa=adresa

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

klienti={}
s.bind(('127.0.0.1',PORT))
print('Server up and listening')

while True:
    data,addr=s.recvfrom(MAX)
    msg=data.decode().split('|')
    if msg[0] == 'registracija':
        ime = msg[1]
        if ime in klienti:
            print('Veke postoi vakov zapis\n')
            s.sendto(('Korisnickoto ime vekje postoi. Izberete drugo!').encode(),addr)
        else:
            lozinka=msg[2]
            role=msg[3]
            korisnik=klient(ime,lozinka,role,addr)
            klienti[ime]=korisnik
            print('Se registrira: ',ime)
            s.sendto(('Uspesna registracija').encode(),addr)

    elif msg[0] == 'porakado':
            korime = msg[1]
            if korime in klienti:
                poraka = msg[2]
                for korisnik in klienti.values():
                    if korisnik.adresa == addr:
                        odkogo = korisnik.ime
                        break
                sender_role = klienti[odkogo].role
                receiver_role = klienti[korime].role
                print('Se ispraka poraka \''+poraka+'\'\n')
                tosend = odkogo +': '+ poraka
                length = len(poraka.encode())
                max_len = 0
                if length > 48:
                    s.sendto("Message too long (max 48B)".encode(), klienti[odkogo].adresa)
                elif sender_role == "user" and receiver_role == "user":
                    max_len = 16
                elif sender_role == "user" and receiver_role == "employee":
                    max_len = 24
                elif sender_role == "employee" and receiver_role == "employee":
                    max_len = 26
                else:
                    max_len = 16

                if length > max_len:
                    exceeded = length - max_len
                    s.sendto(f"Exceeded limit by {exceeded} bytes".encode(), klienti[odkogo].adresa)
                else:
                    s.sendto(f"From {odkogo}: {msg}".encode(), klienti[odkogo].adresa)
                    s.sendto("Message sent".encode(), klienti[odkogo].adresa)

                s.sendto(tosend.encode(), klienti[korime].adresa)

                klienti[korime].dodajPoraka(tosend, odkogo)
                klienti[odkogo].dodajPoraka(tosend, korime)
            else:
                s.sendto((korime + ' ne e  registriran korisnik na server!').encode(), addr)



