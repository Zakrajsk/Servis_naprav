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
                 serijska=None, stroskovno=None, dobavitelj=None, dobava=None, serviser=None, rlp=None, lokacija=None, skrbnik=None):
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
        self.lokacija = lokacija
        self.skrbnik = skrbnik
    
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
                naprava.rlp,
                lokacija.oznaka AS lokacija,
                oseba.ime AS skrbnik
            FROM naprava
                JOIN
                nahajanje ON naprava.inventarna = nahajanje.naprava
                JOIN
                lokacija ON nahajanje.lokacija = lokacija.id
                JOIN
                skrbnistvo ON naprava.inventarna = skrbnistvo.naprava
                JOIN
                oseba ON skrbnistvo.skrbnik = oseba.id
            WHERE inventarna = ?
        """
        cur.execute(sql, [inventarna])
        #naziv, tip, garancija, proizvajalec, serijska, dobava, rlp = cur.fetchone()
        test = cur.fetchone()
        return Naprava(inventarna, *test)
        

    