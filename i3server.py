# Да се напише програма која ќе се користи во една библиотека, така што секој вработен 
# (клиент) кој има своја сметка (account) за кој ќе се чува име и презиме да може да води 
# евиденција за сите членови и нивните изнајмени книги.
# Комуникацијата ќе се одвива на тој начин што вработените најпрво за секој член на 
# библиотеката ќе внесат име, презиме и листа со изнајмени книги. Тие информации ќе се 
# чуваат на сервер. Вработените дополнително да имаат можност за секој член да додадат 
# книга во листата на изнајмени книги (доколку тој изнајми нова книга), да имаат можност да 
# тргнат од листата некоја книга (доколку тој вратил изнајмена книга), да можат да проверат 
# колку вкупно книги има изнајмено и да можат да искомуницираат со друг свој колега, но без 
# пренесување на сложени објекти. Книгите во листите се чуваат само под наслов.
# Во комуникацијата не смее да има изгубени пакети и секој вработен да може да комуницира 
# со својот колега, само ако тој во моментот е активен (на сервер не се чуваат никакви пораки).
# Притоа, истовремено треба да можат и да примаат и пораки од други колеги (клиенти). (35п)

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
members = {}  # key: (ime, prezime), value: [knigi]

def opsluziKlient(sc):
    korime = ""
    while True:
        length = struct.unpack("!i", recv_all(sc, 4))[0]
        data = recv_all(sc, length)
        data = data.decode().split('|')
        
        if data[0] == 'reg':
            korime = data[1]
            l.acquire()
            if korime in users:
                msg = 'nedozvoleno'
            else:
                users[korime] = sc
                msg = 'registered'
            l.release()
            msg_bytes = struct.pack("!i", len(msg)) + msg.encode()
            sc.sendall(msg_bytes)

        elif data[0] == 'poraka' and data[1] in users:
            poraka = korime + ':|' + data[2]
            msg = struct.pack("!i", len(poraka)) + poraka.encode()
            users[data[1]].sendall(msg)

        elif data[0] == 'addmember':
            ime, prezime, knigi_str = data[1], data[2], data[3]
            kluc = (ime, prezime)
            knigi = knigi_str.split(',') if knigi_str else []
            members[kluc] = knigi
            msg = f"Chlen {ime} {prezime} e dodaden so {len(knigi)} knigi."
            sc.sendall(struct.pack("!i", len(msg)) + msg.encode())

        elif data[0] == 'addbook':
            ime, prezime, kniga = data[1], data[2], data[3]
            kluc = (ime, prezime)
            if kluc in members:
                members[kluc].append(kniga)
                msg = f"Dodadena kniga '{kniga}' za {ime} {prezime}."
            else:
                msg = "Chlenot ne postoi."
            sc.sendall(struct.pack("!i", len(msg)) + msg.encode())

        elif data[0] == 'removebook':
            ime, prezime, kniga = data[1], data[2], data[3]
            kluc = (ime, prezime)
            if kluc in members and kniga in members[kluc]:
                members[kluc].remove(kniga)
                msg = f"Knigata '{kniga}' e izbrisana za {ime} {prezime}."
            else:
                msg = "Chlenot ne postoi ili knigata ne e najdena."
            sc.sendall(struct.pack("!i", len(msg)) + msg.encode())

        elif data[0] == 'countbooks':
            ime, prezime = data[1], data[2]
            kluc = (ime, prezime)
            if kluc in members:
                count = len(members[kluc])
                msg = f"{ime} {prezime} ima {count} iznajmeni knigi."
            else:
                msg = "Chlenot ne postoi."
            sc.sendall(struct.pack("!i", len(msg)) + msg.encode())

s.bind(('localhost', PORT))
s.listen(5) # tcp connection oriented (1)
print('server up and listening..')

while True:
    sc, addr = s.accept() #(3)
    threading.Thread(target=opsluziKlient, args=(sc,)).start()