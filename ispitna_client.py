#r-registracija
#n-najava
#b-baranje za prijatelstvo
#pb-prifakjanje na baranje
#vo- vidi objavi 
#ik poraki megju korisnici

import xmlrpc.client as client
import socket, struct, threading

def recv_all(sock, length):
    data = b''
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more:
            raise EOFError('Socket closed')
        data += more
    return data

def chekaj(s):
    s.listen(2)
    while True:
        cs, address = s.accept()
        length = struct.unpack("!i", recv_all(cs, 4))[0]
        data = recv_all(cs, length).decode()
        parts = data.split('|')
        print(f"\n{parts[0]} says: {parts[1]}\n")
        cs.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
proxy = client.ServerProxy('http://127.0.0.1:7001', allow_none=True)

korime = ""

try:
    while True:
        what = input('What is next? [r - reg, n - login, o - logout, b - friend req, pb - accept req, po - post, vo - view posts, ik - msg to user] \nYour choice: ')

        if what == 'r':
            korime = input('Username: ')
            lozinka = input('Password: ')
            print(proxy.registracija(korime, lozinka))

        elif what == 'n':
            korime = input('Username: ')
            lozinka = input('Password: ')
            s.bind(('0.0.0.0', 0))
            threading.Thread(target=chekaj, args=(s,), daemon=True).start()
            local_ip = socket.gethostbyname(socket.gethostname())
            port = s.getsockname()[1]
            print(proxy.najava(korime, lozinka, local_ip, port))

        elif what == 'o':
            print(proxy.odjava(korime))

        elif what == 'b':
            to = input('Send friend request to: ')
            print(proxy.prati_baranje(korime, to))

        elif what == 'pb':
            from_user = input('Accept request from: ')
            print(proxy.prifati_baranje(korime, from_user))

        elif what == 'po':
            tip = input('Type [public/friends/selected]: ')
            tekst = input('Text: ')
            selektirani = []
            if tip == 'selected':
                users = input('Comma separated usernames: ')
                selektirani = users.split(',')
            print(proxy.dodadi_objava(korime, tip, tekst, selektirani))

        elif what == 'vo':
            posts = proxy.get_objavi(korime)
            print("--- Posts visible to you ---")
            for p in posts:
                print(f"From: {p['avtor']} | Type: {p['tip']} | Text: {p['tekst']}")

        elif what == "ik":
            korime_p = input("Which user? ")
            poraka = input("What message? ")
            result = proxy.isprati_do_korisnik(korime_p, korime)
            
            if isinstance(result, list) or isinstance(result, tuple):
                adresa, porta = result
                try:
                    sv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sv.connect((adresa, int(porta)))
                    poraka_full = korime + "|" + poraka
                    sv.sendall(struct.pack("!i", len(poraka_full)) + poraka_full.encode())
                    sv.close()
                    print(f"Message sent to {korime_p}")
                except Exception as e:
                    print("Error while sending:", e)
            else:
                print("Error:", result) 
                
except KeyboardInterrupt:
    print("\nClient terminated")
