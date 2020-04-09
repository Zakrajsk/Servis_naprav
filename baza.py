import csv

class Tabela():
    """
    Tabela, ki predstavlja tabelo v bazi
    ime - ime tabele
    podatki - ime datoteke s podatki
    """
    ime = None
    podatki = None

    def __init__(self, conn):
        self.conn = conn

    def ustvari(self):
        """
        Metoda za ustvarjanje tabel, ki jo mora podrazred povoziti
        """
        raise NotImplementedError
    
    def izbrisi(self):
        """
        Izbrise trenutno tabelo
        """
        self.conn.execute("DROP TABLE IF EXISTS {0};".format(self.ime))

    def uvozi(self, encoding="UTF-8"):
        """
        Uvozi podatke z datoteke v bazo
        """
        if self.podatki == None:
            return
        with open(self.podatki, encoding=encoding) as datoteka:
            podatki = csv.reader(datoteka)
            stolpci = self.pretvori(next(podatki))
            poizvedba = self.dodajanje(stolpci)
            for vrstica in podatki:
                vrstica = [None if x == "x" else x for x in vrstica]
                self.dodaj_vrstico(vrstica, poizvedba)

    def izprazni(self):
        """
        Izprazni tabelo
        """
        self.conn.execute("DELETE FROM {0}".format(self.ime))

    @staticmethod
    def pretvori(stolpci):
        """
        Pretvori imena stolpcev na ustrezno obliko
        """
        return stolpci
    
    def dodajanje(self, stolpci=None, stevilo=None):
        """
        Metoda za grajenje poizvedbe za dodajanje
        """
        if stolpci is None:
            assert stevilo is not None
            st = ""
        else:
            st = " ({0})".format(", ".join(stolpci))
            stevilo = len(stolpci)
            return "INSERT INTO {0}{1} VALUES ({2})".format(self.ime, st, ", ".join(["?"] * stevilo))
    
    def dodaj_vrstico(self, podatki, poizvedba=None):
        """
        Metoda za dodajanje vrstice
        """
        if poizvedba is None:
            poizvedba = self.dodajanje(stevilo=len(podatki))
            cur = self.conn.execute(poizvedba, podatki)
            return cur.lastrowid

class Naprava(Tabela):
    """
    Tabela za naprave
    """
    ime = "naprave"
    podatki = "podatki/naprave.csv"

    def __init__(self, conn):
        super().__init__(conn)
    
    def ustvari(self):
        """
        Ustvari tabelo naprave
        """
        self.conn.execute("""
        CREATE TABLE Naprava (
            Inventarna   INTEGER PRIMARY KEY,
            Naziv        TEXT    NOT NULL,
            Tip          TEXT    NOT NULL,
            Garancija    DATE,
            Proizvajalec TEXT,
            Serijska     TEXT    NOT NULL
                                UNIQUE,
            Dobavitelj   INTEGER REFERENCES Podjetje (Id),
            Dobava       DATE,
            Stroskovno   TEXT    REFERENCES Stroskovno_mesto (Oznaka),
            RLP          INTEGER CHECK (RLP IN (12, 18, 24))
            )
        """)

    def uvozi(self, encoding="UTF-8"):
        """
        Uvozi podatke o napravah
        """
        super().uvozi(encoding=encoding)
    
def ustvari_tabele(tabele):
    """
    Ustvari podane tabele
    """
    for t in tabele:
        t.ustvari()

def izbrisi_tabele(tabele):
    """
    Izbrise podane tabele
    """
    for t in tabele:
        t.izbrisi()

def uvozi_podatke(tabele):
    """
    Uvozi podatke v dane tabele
    """
    for t in tabele:
        t.uvozi()

def izprazni_tabele(tabele):
    """
    Izprazne podane tabele
    """
    for t in tabele:
        t.izprazni()

def ustvari_bazo(conn):
    """
    Izvede ustvarjanje baze
    """
    tabele = pripravi_tabele(conn)
    izbrisi_tabele(tabele)
    ustvari_tabele(tabele)
    uvozi_podatke(tabele)

def pripravi_tabele(conn):
    """
    Pripravi objekte za tabele
    """
    naprava = Naprava(conn)
    return [naprava]

def ustvari_bazo_ce_ne_obstaja(conn):
    """
    Ustvari bazo, ce ta ne obstaja
    """
    with conn:
        cur = conn.execute("SELECT COUNT(*) FROM sqlite_master")
        if cur.fetchone() == (0, ):
            ustvari_bazo(conn)
    