import baza
import sqlite3

conn = sqlite3.connect('naprave.db')
baza.ustvari_bazo_ce_ne_obstaja(conn)
conn.execute('PRAGMA foreign_keys = ON')

stroskovno_mesto, naprava, podjetje, oseba, skrbnistvo, lokacija, nahajanje, popravilo = baza.pripravi_tabele(conn)

class Naprava:
    """
    Razred za napravo
    """

    insert = naprava.dodajanje(["inventarna", "naziv", "tip"])

    def __init__(self, inventarna, naziv, tip=None, garancija=None, proizvajalec=None,
                 serijska=None, stroskovno=None, dobavitelj=None, dobava=None, serviser=None, rlp=None):
        """
        Konstruktor naprave
        """
        self.inventarna = inventarna
        self.naziv = naziv
        self.tip = tip
        self.garancija = garancija
        self.proizvajalec = proizvajalec
        self.serijska = serijska
        self.stroskovno = stroskovno
        self.dobavitelj = dobavitelj
        self.dobava = dobava
        self.serviser = serviser
        self.rlp = rlp
    
    @staticmethod
    def opis_naprave(inventarna):
        """
        Vrne napravo z vsemi ustreznimi podatki za opis naprave
        """
        cur = conn.cursor()
        sql = """
            SELECT naprava.naziv,
                naprava.tip,
                naprava.garancija,
                naprava.proizvajalec,
                naprava.serijska,
                naprava.stroskovno,
                naprava.dobavitelj,
                naprava.dobava,
                naprava.serviser,
                naprava.rlp
            FROM naprava
            WHERE inventarna = ?
        """
        cur.execute(sql, [inventarna])
        rez = cur.fetchone()
        return Naprava(inventarna, *rez)

    @staticmethod
    def vrni_naziv(inventarna):
        """
        Vrne naziv naprave
        """
        cur = conn.cursor()
        sql = """
            SELECT naprava.naziv
            FROM naprava
            WHERE inventarna = ?
        """
        cur.execute(sql, [inventarna])
        rez = cur.fetchone()
        return rez[0]
        

class Popravilo:
    """
    Razred za popravilo
    """

    insert = popravilo.dodajanje(["st_narocila", "tip", "opis", "naprava"])

    def __init__(self, st_narocila=None, tip=None, opis=None, naprava=None, aktivacija=None, sprejem=None, vrnitev=None, zakljucek=None):
        """
        Konstruktor popravila
        """
        self.st_narocila = st_narocila
        self.tip = tip
        self.opis = opis
        self.naprava = naprava
        self.aktivacija = aktivacija
        self.sprejem = sprejem
        self.vrnitev = vrnitev
        self.zakljucek = zakljucek

    @staticmethod
    def vrni_popravila(inventarna):
        """
        Vrne vsa popravila naprave z inventarno
        """
        sql = """
            SELECT aktivacija,
                tip,
                sprejem,
                vrnitev,
                zakljucek,
                opis
            FROM popravilo
            WHERE naprava = ?
            ORDER BY substr(aktivacija, 7) || substr(aktivacija, 4, 2) || substr(aktivacija, 1, 2) DESC
        """
        for aktivacija, tip, sprejem, vrnitev, zakljucek, opis in conn.execute(sql, [inventarna]):
            yield Popravilo(aktivacija=aktivacija, tip=tip, sprejem=sprejem, vrnitev=vrnitev, zakljucek=zakljucek, opis=opis)


class Nahajanje:
    """
    Razred za nahajanje
    """

    inset = nahajanje.dodajanje(["od", "do"])

    def __init__(self, od=None, do=None, naprava=None, lokacija=None):
        """
        Konstruktor nahajanja
        """
        self.od = od
        self.do = do
        self.naprava = naprava
        self.lokacija = lokacija

    @staticmethod
    def zadnja_lokacija(inventarna):
        """
        Vrne zadnjo lokacijo naprave z inventarno stevilo
        """
        cur = conn.cursor()
        sql = """
            SELECT lokacija.oznaka
            FROM lokacija
                JOIN
                nahajanje ON lokacija.id = nahajanje.lokacija
            WHERE nahajanje.naprava = ?
            ORDER BY substr(nahajanje.od, 7) || substr(nahajanje.od, 4, 2) || substr(nahajanje.od, 1, 2) DESC
            LIMIT 1
        """
        cur.execute(sql, [inventarna])
        rez = cur.fetchone()
        return rez[0]
        

    @staticmethod
    def odtujenosti(inventarna):
        """
        Vrne vse datume odtujenosti in vrnitve
        """
        sql = """
            SELECT nahajanje.od,
                nahajanje.[do]
            FROM nahajanje
                JOIN
                lokacija ON nahajanje.lokacija = lokacija.id
            WHERE naprava = ? AND 
                lokacija.oznaka = "ODTUJENA"
            ORDER BY substr(nahajanje.od, 7) || substr(nahajanje.od, 4, 2) || substr(nahajanje.od, 1, 2) DESC
        """
        for od, do in conn.execute(sql, [inventarna]):
            yield Nahajanje(od, do)


class Oseba:
    """
    Razred za osebo
    """

    insert = oseba.dodajanje(["ime"])

    def __init__(self, ime, telefon=None, email=None):
        """
        Konstruktor osebe
        """
        self.ime = ime
        self.telefon = telefon
        self.email = email

    @staticmethod
    def zadnji_skrbnik(inventarna):
        """
        Vrne zadnjega skrbnika naprave z inventarno
        """
        cur = conn.cursor()
        sql = """
        SELECT oseba.ime
        FROM oseba
            JOIN
            skrbnistvo ON oseba.id = skrbnistvo.skrbnik
        WHERE skrbnistvo.naprava = ?
        ORDER BY substr(skrbnistvo.od, 7) || substr(skrbnistvo.od, 4, 2) || substr(skrbnistvo.od, 1, 2) DESC
        LIMIT 1
        """
        cur.execute(sql, [inventarna])
        rez = cur.fetchone()
        return rez[0]


    