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

from xmlrpc.server import SimpleXMLRPCServer
import socket,struct,threading

class korisnik():
    def __init__(self,korime, lozinka, adresa=0, porta=0, uloga=' ', najaven=0, dop_info=''):
        self.korime, self.lozinka, self.adresa, self.porta, self.uloga, self.najaven, self.dop_info = korime, lozinka, adresa, porta, uloga, najaven, dop_info

class grupa():
    def __init__(self, ime):
        self.ime = ime
        self.korisnici = dict()

korisnici = {}
grupi = {}

def registracija(korime, lozinka, uloga, dop_info=''):
    if korime in korisnici:
        return "Korisnickoto ime e zafateno"
    else:
        korisnici[korime] = korisnik(korime, lozinka, uloga=uloga, dop_info=dop_info)
        return "Uspeshna registracija"
    
def najava(korime, lozinka, ipaddr, port):
    if korime in korisnici and korisnici[korime].lozinka == lozinka:
        korisnici[korime].adresa = ipaddr
        korisnici[korime].porta = port
        korisnici[korime].najaven = 1

        return "Uspeshna najava"
    else:
        return "Gresna lozinka ili korisnicko ime!"
    
def odjava(korime):
    if korime in korisnici:
        del korisnici[korime]
        for grupa in grupi:
            if korime in grupa.korisnici:
                del grupa.korisnici[korime]
        return "Uspesno se odjavivte od server"
    else:
        return "Nepostoecki korisnik"

def kreiraj_grupa(ime, korime):
    if ime == "administracija":
        if ime in grupi:
            return "Grupata 'administracija' vekje postoi."
        if korisnici[korime].uloga != 'administrator':
            return "Samo administrator moze da ja kreira grupata 'administracija'."
        grupi[ime] = grupa(ime)
        grupi[ime].korisnici[korime] = korisnici[korime]
        return "Uspeshno kreirana grupa 'administracija'."
    else:
        if korisnici[korime].uloga != 'administrator':
            return "Samo administrator moze da kreira grupa."
        grupi[ime] = grupa(ime)
        return f"Uspeshno kreirana grupa '{ime}'."


def prikluci_grupa(ime_grupa, korime):
    if ime_grupa not in grupi:
        return "Taa grupa ne postoi."
    
    korisnik_obj = korisnici[korime]
    
    if ime_grupa == "administracija":
        if korisnik_obj.uloga != "administrator":
            return "Samo administratori mozat da se priklucat vo 'administracija'."
    elif korisnik_obj.dop_info != ime_grupa:
        return f"Ne moze da se prikluci vo grupata '{ime_grupa}' bidejki dopolnitelnata informacija {korisnik_obj.dop_info} ne odgovara."
    
    grupi[ime_grupa].korisnici[korime] = korisnik_obj
    return f"{korime} e priklucen vo grupata {ime_grupa}."

def napusti_grupa(ime, korime):
    if ime in grupi:
        del grupi[ime].korisnici[korime]
        return "Uspesno ja napustivte grupata!"
    else:
        "Nema takva grupa!"

def isprati_korisnik(korime, korime_k):
    if korime_k not in korisnici or korisnici[korime_k].najaven == 0:
        return "Ne ste najaveni/registirani"
    if korime in korisnici and korisnici[korime].najaven:
        return korisnici[korime].adresa, korisnici[korime].porta
    else:
        return "Korisnikot ne e najaven/registriran"

def isprati_grupa(ime, korime_k):
    if ime not in grupi:
        return "Takva grupa ne postoi!"
    if korime_k in grupi[ime].korisnici and korisnici[korime_k].najaven:
        return grupi[ime].korisnici
    else:
        return "Ne ste del od grupata/ne ste najaveni"

server = SimpleXMLRPCServer(('127.0.0.1',7001))
server.register_multicall_functions()
server.register_introspection_functions()
server.register_function(registracija)
server.register_function(najava)
server.register_function(odjava)
server.register_function(prikluci_grupa)
server.register_function(napusti_grupa)
server.register_function(kreiraj_grupa)
server.register_function(isprati_korisnik)
server.register_function(isprati_grupa)

print('Server up and listening..')
server.serve_forever()
