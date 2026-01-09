from xmlrpc.server import SimpleXMLRPCServer

class Korisnik:
    def __init__(self, korime, lozinka, adresa=0, porta=0, najaven=0):
        self.korime = korime
        self.lozinka = lozinka
        self.adresa = adresa
        self.porta = porta
        self.najaven = najaven

korisnici = {}
prijateli = {}
baranja = {}
objavi = []

def registracija(korime, lozinka):
    if korime in korisnici:
        return 'Username already taken'
    korisnici[korime] = Korisnik(korime, lozinka)
    prijateli[korime] = set()
    baranja[korime] = set()
    return 'Registration successful'

def najava(korime, lozinka, interface, port):
    if korime in korisnici and korisnici[korime].lozinka == lozinka:
        korisnici[korime].najaven = 1
        korisnici[korime].adresa = interface
        korisnici[korime].porta = int(port)  
        return 'Login successful'
    return 'Wrong username or password'

def odjava(korime):
    if korime in korisnici:
        korisnici[korime].najaven = 0
        return 'Logged out'
    return 'User not found'

def prati_baranje(od, do):
    if do in korisnici:
        baranja[do].add(od)
        return f'Request sent to {do}'
    return 'User not found'

def prifati_baranje(do, od):
    if od in baranja[do]:  
        baranja[do].remove(od)
        prijateli[do].add(od)
        prijateli[od].add(do)
        return f'Now friends with {od}'
    return 'No such request'

def isprati_do_korisnik(korimep, korime):
    if korime not in korisnici or korisnici[korime].najaven == 0:
        return "You are not logged in"
    if korimep in prijateli[korime] and korisnici[korimep].najaven:
        return korisnici[korimep].adresa, korisnici[korimep].porta
    return "Not friends or user not online"

def dodadi_objava(avtor, tip, tekst, selektirani):
    if tip not in ["public", "friends", "selected"]:
        return "Invalid post type"
    objava = {"avtor": avtor, "tip": tip, "tekst": tekst, "za": selektirani}
    objavi.append(objava)
    return "Post added"

def get_objavi(korime):
    visible = []
    for o in objavi:
        if o['tip'] == 'public':
            visible.append(o)
        elif o['tip'] == 'friends' and korime in prijateli.get(o['avtor'], []):
            visible.append(o)
        elif o['tip'] == 'selected' and korime in o['za']:
            visible.append(o)
        elif o['avtor'] == korime:
            visible.append(o)
    return visible

server = SimpleXMLRPCServer(('127.0.0.1', 7001), allow_none=True)
server.register_function(registracija)
server.register_function(najava)
server.register_function(odjava)
server.register_function(prati_baranje)
server.register_function(prifati_baranje)
server.register_function(isprati_do_korisnik)
server.register_function(dodadi_objava)
server.register_function(get_objavi)
print("Server ready")
server.serve_forever()
