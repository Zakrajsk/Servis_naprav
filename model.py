import baza
import sqlite3

conn = sqlite3.connect('naprave.db')
baza.ustvari_bazo_ce_ne_obstaja(conn)
conn.execute('PRAGMA foreign_keys = ON')

stroskovno_mesto, naprava, podjetje, oseba, skrbnistvo, lokacija, nahajanje, popravilo, faza = baza.pripravi_tabele(conn)

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
    def __init__(self, st_narocila, tip, opis, naprava):
        """
        Konstruktor popravila
        """
        self.st_narocila = st_narocila
        self.tip = tip
        self.opis = opis
        self.naprava = naprava

    @staticmethod
    def vrni_popravila(inventarna):
        """
        Vrne vsa popravila naprave z inventarno za opis naprave
        """
        sql = """
            SELECT popravilo.st_narocila,
                popravilo.tip,
                popravilo.opis,
                faza.datum as aktivacija
            FROM popravilo
                JOIN 
                faza ON popravilo.st_narocila = faza.popravilo
            WHERE popravilo.naprava = ? AND faza.stopnja = 'aktivacija'
            ORDER BY substr(aktivacija, 7) || substr(aktivacija, 4, 2) || substr(aktivacija, 1, 2) DESC
        """
        for st_narocila, tip, opis, aktivacija in conn.execute(sql, [inventarna]):
            yield {'tip': tip, 'opis': opis, 'aktivacija': aktivacija,
            'sprejem': Faza.datum_stopnje('sprejem', st_narocila),
            'vrnitev': Faza.datum_stopnje('vrnitev', st_narocila)}
    
    def dodaj_v_bazo(self):
        insert = popravilo.dodajanje(["st_narocila", "tip", "opis", "naprava"])
        with conn:
            popravilo.dodaj_vrstico([self.st_narocila, self.tip, self.opis, self.naprava], insert)

    @staticmethod
    def aktivna_popravila(inventarna):
        """
        Vrne stevilo in tabelo vseh aktivnih popravil, ki so na stopnji aktivacije
        """
        tabela_popravil = list()
        sql = """
            SELECT faza.popravilo
            FROM faza
                JOIN
                popravilo ON faza.popravilo = popravilo.st_narocila
            WHERE popravilo.naprava = ?
            GROUP BY faza.popravilo
            HAVING count(faza.popravilo) = 1;
        """
        for popravilo in conn.execute(sql, [inventarna]):
            tabela_popravil.append(popravilo[0])
        return (len(tabela_popravil), tabela_popravil)

    @staticmethod
    def prevzeta_popravila(inventarna):
        """
        Vrne stevilo in tabelo vseh popravil, ki so bila prevzeta
        """
        tabela_popravil = list()
        sql = """
            SELECT faza.popravilo
            FROM faza
                JOIN
                popravilo ON faza.popravilo = popravilo.st_narocila
            WHERE popravilo.naprava = ?
            GROUP BY faza.popravilo
            HAVING count(faza.popravilo) = 2;
        """
        for popravilo in conn.execute(sql, [inventarna]):
            tabela_popravil.append(popravilo[0])
        return (len(tabela_popravil), tabela_popravil)

    @staticmethod
    def vrnjena_popravila(inventarna):
        """
        Vrne stevilo in tabelo vseh popravil, ki so bila prevzeta
        """
        tabela_popravil = list()
        sql = """
            SELECT faza.popravilo
            FROM faza
                JOIN
                popravilo ON faza.popravilo = popravilo.st_narocila
            WHERE popravilo.naprava = ?
            GROUP BY faza.popravilo
            HAVING count(faza.popravilo) = 3;
        """
        for popravilo in conn.execute(sql, [inventarna]):
            tabela_popravil.append(popravilo[0])
        return (len(tabela_popravil), tabela_popravil)


class Faza:
    """
    Razred za fazo
    """
    def __init__(self, stopnja, popravilo, datum=None):
        """
        Konstruktor faze
        """
        self.stopnja = stopnja
        self.popravilo = popravilo
        self.datum = datum
        
    @staticmethod
    def datum_stopnje(stopnja, popravilo):
        """
        Vrne datum stopnje popravilo
        """
        cur = conn.cursor()
        sql = """
            SELECT datum
            FROM faza
            WHERE popravilo = ? AND stopnja = ?
        """
        cur.execute(sql, [popravilo, stopnja])
        rez = cur.fetchone()
        return '' if rez == None else rez[0]

    def dodaj_v_bazo(self):
        """
        V bazo doda novo stopnjo popravila z dolocenim datumom
        """
        insert = faza.dodajanje(['datum', 'stopnja', 'popravilo'])
        with conn:
            faza.dodaj_vrstico([self.datum, self.stopnja, self.popravilo], insert)



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
            if do == None:
                do = ''
            yield Nahajanje(od, do)


class Lokacija:
    """
    Razred za lokacijo
    """
    def __init(self, oznaka):
        """
        Konstruktor lokacije
        """
        self.oznaka = oznaka

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
    def seznam_lokacij():
        """
        Vrne seznam vseh lokacij v bazi
        """
        tabela_lokacij = list()
        conn.cursor()
        sql = """
            SELECT oznaka
            FROM lokacija
            ORDER BY oznaka
        """
        for oznaka in conn.execute(sql):
            tabela_lokacij.append(oznaka[0])
        return tabela_lokacij



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


class Datum():
    """
    Razred za delo z datumi
    """

    def __init__(self, dan, mesec, leto):
        """
        Konstruktor za datum
        """
        self.dan = dan
        self.mesec = mesec
        self.leto = leto

    @staticmethod
    def pretvori_v_niz(dan, mesec, leto):
        """
        Pretvori datum v niz za v bazo v format dd.mm.yyyy
        """
        niz_dan = dan if int(dan) >= 10 else ('0' + dan)
        niz_mesec = mesec if int(mesec) >= 10 else ('0' + mesec)
        return '.'.join([niz_dan, niz_mesec, leto])


    