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

def recv_all(sock, length):
    data = b''
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more:
            raise EOFError(f'Socket closed with {len(data)} bytes received, expected {length}')
        data += more
    return data

def listener(s):
    while True:
        try:
            length = struct.unpack("!i", recv_all(s, 4))[0]
            data = recv_all(s, length).decode()
            print('\n[PRIMENO] ' + data)
        except:
            print("Прекината конекција.")
            break

def send_msg(sock, msg):
    msg = msg.encode()
    full = struct.pack("!i", len(msg)) + msg
    sock.sendall(full)

s = socket(AF_INET, SOCK_STREAM)
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
PORT = 6789
s.connect(('localhost', PORT))

uname = input('Внеси корисничко име (уникатно):\n')
send_msg(s, f'reg|{uname}')

threading.Thread(target=listener, args=(s,), daemon=True).start()

print("\n--- Команди ---")
print("addmember|ime prezime|book1,book2,...")
print("addbook|ime prezime|booktitle")
print("removebook|ime prezime|booktitle")
print("countbooks|ime prezime")
print("msg|receiver_username|your message")
print("exit\n")

while True:
    try:
        cmd = input(">> ")
        if cmd == "exit":
            print("Исклучување...")
            s.close()
            break
        send_msg(s, cmd)
    except KeyboardInterrupt:
        print("Излез.")
        s.close()
        break
