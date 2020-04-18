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

    def uvozi(self, encoding="UTF-8", **kwargs):
        """
        Uvozi podatke z datoteke v bazo
        """
        if self.podatki == None:
            return
        with open(self.podatki, encoding=encoding) as datoteka:
            podatki = csv.reader(datoteka)
            stolpci = self.pretvori(next(podatki), kwargs)
            poizvedba = self.dodajanje(stolpci)
            for vrstica in podatki:
                vrstica = [None if x == "x" else x for x in vrstica]
                self.dodaj_vrstico(vrstica, poizvedba, **kwargs)

    def izprazni(self):
        """
        Izprazni tabelo
        """
        self.conn.execute("DELETE FROM {0}".format(self.ime))

    @staticmethod
    def pretvori(stolpci, kwargs):
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
    
    def dodaj_vrstico(self, podatki, poizvedba=None, **kwargs):
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
    ime = "naprava"
    podatki = "podatki/naprave.csv"

    def __init__(self, conn, stroskovno_mesto):
        super().__init__(conn)
        self.stroskovno_mesto = stroskovno_mesto
    
    def ustvari(self):
        """
        Ustvari tabelo naprave
        """
        self.conn.execute("""
            CREATE TABLE naprava (
                inventarna   INTEGER PRIMARY KEY,
                naziv        TEXT    NOT NULL,
                tip          TEXT    NOT NULL,
                garancija    DATE,
                proizvajalec TEXT,
                serijska     TEXT    NOT NULL
                                    UNIQUE,
                dobavitelj   TEXT REFERENCES Podjetje (naziv),
                dobava       DATE,
                stroskovno   TEXT    REFERENCES Stroskovno_mesto (oznaka),
                rlp          INTEGER CHECK (RLP IN (12, 18, 24))
            );
        """)

    def uvozi(self, encoding="UTF-8"):
        """
        Uvozi podatke o napravah
        """
        insert = self.stroskovno_mesto.dodajanje(stevilo=1)
        super().uvozi(encoding=encoding, insert=insert)
    
    @staticmethod
    def pretvori(stolpci, kwargs):
        """
        Zapomni si indeks stolpca z stroskovnim mestom
        """
        kwargs["stroskovno_mesto"] = stolpci.index("stroskovno")
        return stolpci
    
    def dodaj_vrstico(self, podatki, poizvedba=None, insert=None, stroskovno_mesto=None):
        """
        Dodaj napravo in pripadajoce stroskovno mesto
        """
        if stroskovno_mesto is not None:
            if insert is None:
                insert = self.stroskovno_mesto.dodajanje(1)
            if podatki[stroskovno_mesto] is not None:
                self.stroskovno_mesto.dodaj_vrstico([podatki[stroskovno_mesto]], insert)
        return super().dodaj_vrstico(podatki, poizvedba)


class StroskovnoMesto(Tabela):
    """
    Tabela za stroskovna mesta
    """
    ime = "stroskovno_mesto"

    def ustvari(self):
        """
        Ustvari tabelo stroskovno_mesto
        """
        self.conn.execute("""
            CREATE TABLE stroskovno_mesto (
                oznaka TEXT PRIMARY KEY
            );
        """)
    
    def dodaj_vrstico(self, podatki, poizvedba=None):
        """
        Dodaj stroskovno mesto
        Če ta obstaja ga ne dodamo še enkrat
        """
        cur = self.conn.execute("""
            SELECT oznaka FROM stroskovno_mesto
            WHERE oznaka = ?;
        """, podatki)
        r = cur.fetchone()
        if r is None:
            return super().dodaj_vrstico(podatki, poizvedba)


class Podjetje(Tabela):
    """
    Tabela za podjetja
    """
    ime="podjetje"
    podatki="podatki/podjetja.csv"

    def ustvari(self):
        """
        Ustvari tabelo podjetje
        """
        self.conn.execute("""
            CREATE TABLE podjetje (
                naziv TEXT PRIMARY KEY,
                telefon TEXT UNIQUE,
                email TEXT UNIQUE
            );
        """)


class Oseba(Tabela):
    """
    Tabela za osebe
    """
    ime="oseba"
    podatki="podatki/osebe.csv"

    def ustvari(self):
        """
        Ustvari tabelo osebe
        """
        self.conn.execute("""
            CREATE TABLE oseba (
                id INTEGER PRIMARY KEY,
                ime TEXT NOT NULL,
                telefon TEXT UNIQUE,
                email TEXT UNIQUE
            );
        """)
    

class Skrbnistvo(Tabela):
    """
    Tabela za podatke o skrbnistvu
    """
    ime="skrbnistvo"
    podatki="podatki/skrbnistva.csv"

    def ustvari(self):
        """
        Ustvari tabelo skrbnistvo
        """
        self.conn.execute("""
            CREATE TABLE skrbnistvo(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                od DATE NOT NULL,
                [do] DATE,
                skrbnik INTERGER REFERENCES oseba (id),
                naprava INTEGER REFERENCES naprava (inventarna)
            );
        """)


class Lokacija(Tabela):
    """
    Tabela za podatko lokacij
    """
    ime="lokacija"
    
    def ustvari(self):
        """
        Ustvari tabelo lokacija
        """
        self.conn.execute("""
            CREATE TABLE lokacija (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                oznaka TEXT UNIQUE
            );
        """)
    
    def dodaj_vrstico(self, podatki, poizvedba=None):
        """
        Doda lokacijo
        Če lokacija že obstaja vrne njen id
        """
        cur = self.conn.execute("""
            SELECT id FROM lokacija
            WHERE oznaka = ?;
        """, podatki)
        r = cur.fetchone()
        if r is None:
            return super().dodaj_vrstico(podatki, poizvedba)
        else:
            return r[0]
            

class Nahajanje(Tabela):
    """
    Tabela za nahajanje naprav na neki lokaciji
    """
    ime = "nahajanje"
    podatki = "podatki/nahajanja.csv"

    def __init__(self, conn, lokacija):
        """
        Konstruktor tabele nahajanja
        """
        super().__init__(conn)
        self.lokacija = lokacija
    
    def ustvari(self):
        """
        Ustvari tabelo nahajanje
        """
        self.conn.execute("""
            CREATE TABLE nahajanje (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                od DATE NOT NULL,
                [do] DATE,
                naprava INTEGER REFERENCES naprava (inventarna),
                lokacija INTEGER REFERENCES lokacija (id)
            );
        """)

    def uvozi(self, encoding="UTF-8"):
        """
        Uvozi nahajanja in pripadajoče lokacije
        """
        insert = self.lokacija.dodajanje(["oznaka"])
        super().uvozi(encoding=encoding, insert=insert)

    @staticmethod
    def pretvori(stolpci, kwargs):
        """
        spremeni ime stolpca z zanrom
        in si zapomni njegov indeks
        """
        kwargs["oznaka"] = stolpci.index("lokacija")
        return stolpci

    def dodaj_vrstico(self, podatki, poizvedba=None, insert=None, oznaka=None):
        """
        Dodaj nahajanja in pripadajočo lokacijo
        """
        assert oznaka is not None
        if insert is None:
            insert = self.lokacija.dodajanje(["oznaka"])
        podatki[oznaka] = self.lokacija.dodaj_vrstico([podatki[oznaka]], insert)
        return super().dodaj_vrstico(podatki, poizvedba)


class Popravilo(Tabela):
    """
    Tabela za popravila
    """
    ime="popravilo"
    podatki="podatki/popravila.csv"

    def ustvari(self):
        """
        Ustvari tabelo popravila
        """
        self.conn.execute("""
            CREATE TABLE popravilo (
                st_narocila INTEGER PRIMARY KEY,
                tip         TEXT    NOT NULL
                                    CHECK (tip IN ('RLP', 'Popravilo', 'Popravilo in RLP') ),
                opis        TEXT,
                naprava     INTEGER REFERENCES naprava (inventarna),
                servis      TEXT REFERENCES podjetje (naziv),
                aktivacija DATE NOT NULL,
                sprejem DATE,
                vrnitev DATE,
                zakljucek DATE
            );
        """)


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
    stroskovno_mesto = StroskovnoMesto(conn)
    naprava = Naprava(conn, stroskovno_mesto)
    podjetje = Podjetje(conn)
    oseba = Oseba(conn)
    skrbnistvo = Skrbnistvo(conn)
    lokacija = Lokacija(conn)
    nahajanje = Nahajanje(conn, lokacija)
    popravilo = Popravilo(conn)
    return [stroskovno_mesto, naprava, podjetje, oseba, skrbnistvo, lokacija, nahajanje, popravilo]

def ustvari_bazo_ce_ne_obstaja(conn):
    """
    Ustvari bazo, ce ta ne obstaja
    """
    with conn:
        cur = conn.execute("SELECT COUNT(*) FROM sqlite_master")
        if cur.fetchone() == (0, ):
            ustvari_bazo(conn)
