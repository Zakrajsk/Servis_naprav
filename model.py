from os import stat
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
                 serijska=None, dobavitelj=None, dobava=None, serviser=None, stroskovno=None, rlp=None):
        """
        Konstruktor naprave
        """
        self.inventarna = inventarna
        self.naziv = naziv
        self.tip = tip
        self.garancija = garancija
        self.proizvajalec = proizvajalec
        self.serijska = serijska
        self.dobavitelj = dobavitelj
        self.dobava = dobava
        self.serviser = serviser
        self.stroskovno = stroskovno
        self.rlp = rlp
    
    @staticmethod
    def ali_obstaja(inventarna):
        """
        Vrne true, ce naprava obstaja drugace pa false
        """
        cur = conn.cursor()
        sql = """
            SELECT naprava.inventarna
            FROM naprava
            WHERE inventarna = ?
        """
        cur.execute(sql, [inventarna])
        rez = cur.fetchone()
        return True if rez != None else False


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
                naprava.dobavitelj,
                naprava.dobava,
                naprava.serviser,
                naprava.stroskovno,
                naprava.rlp
            FROM naprava
            WHERE inventarna = ?
        """
        cur.execute(sql, [inventarna])
        rez = cur.fetchone()
        return Naprava(inventarna, *rez) if rez != None else None
    
    @staticmethod
    def vse_za_izpis(sortiraj_po):
        """
        Vrne tabele vseh naprav predstavljeno s slovarjem, ki niso odtujene
        """
        cur = conn.cursor()
        sql = """
            SELECT naprava.inventarna,
                naprava.naziv,
                naprava.tip,
                naprava.serijska,
                naprava.serviser,
                naprava.rlp,
                naprava.dobava,
                lokacija.oznaka
            FROM naprava
                JOIN
                nahajanje ON naprava.inventarna = nahajanje.naprava
                JOIN
                lokacija ON lokacija.id = nahajanje.lokacija
            WHERE nahajanje.[do] IS NULL AND 
                lokacija.oznaka NOT LIKE 'ODTUJENA'
            ORDER BY
        """ + sortiraj_po + ";"
        tabela_ustreznih = list()
        st = 1
        for inventarna, naziv, tip, serijska, serviser, rlp, dobava, lokacija in cur.execute(sql):
            if lokacija == "ODPISANA" or lokacija == "ODTUJENA" or lokacija == "POSTOPEK ODPISA":
                continue
            temp_naprava = {'Št': st, 'Inventarna': inventarna, 'Naziv': naziv, 'Tip' : tip, 'Serijska': serijska,
                            'Servis': serviser, 'RLP': rlp, 'Dobava': dobava, 'Lokacija': lokacija}
            tabela_ustreznih.append(temp_naprava)
            st += 1
        return tabela_ustreznih

    @staticmethod
    def vse_za_rlp_izpis(sortiraj_po):
        """
        Vrne tabele vseh naprav predstavljeno s slovarjem, ki niso odtujene
        """
        cur = conn.cursor()
        sql = """
            SELECT naprava.inventarna,
                naprava.naziv,
                naprava.tip,
                naprava.serijska,
                naprava.serviser,
                naprava.rlp,
                naprava.dobava,
                lokacija.oznaka
            FROM naprava
                JOIN
                nahajanje ON naprava.inventarna = nahajanje.naprava
                JOIN
                lokacija ON lokacija.id = nahajanje.lokacija
            WHERE nahajanje.[do] IS NULL AND 
                lokacija.oznaka NOT LIKE 'ODTUJENA' AND
                naprava.rlp NOT LIKE '-'
            ORDER BY
        """ + sortiraj_po + ";"
        tabela_ustreznih = list()
        for inventarna, naziv, tip, serijska, serviser, rlp, dobava, lokacija in cur.execute(sql):
            if lokacija == "ODPISANA" or lokacija == "ODTUJENA" or lokacija == "POSTOPEK ODPISA":
                continue
            temp_naprava = {'Inventarna': inventarna, 'Naziv': naziv, 'Tip' : tip, 'Serijska': serijska,
                            'Servis': serviser, 'RLP': rlp, 'Dobava': dobava, 'Lokacija': lokacija}
            tabela_ustreznih.append(temp_naprava)
        return tabela_ustreznih

    @staticmethod
    def vse_brez_rlp_izpis(sortiraj_po):
        """
        Vrne tabele vseh naprav predstavljeno s slovarjem, ki niso odtujene
        """
        cur = conn.cursor()
        sql = """
            SELECT naprava.inventarna,
                naprava.naziv,
                naprava.tip,
                naprava.serijska,
                naprava.serviser,
                naprava.rlp,
                naprava.dobava,
                lokacija.oznaka
            FROM naprava
                JOIN
                nahajanje ON naprava.inventarna = nahajanje.naprava
                JOIN
                lokacija ON lokacija.id = nahajanje.lokacija
            WHERE nahajanje.[do] IS NULL AND 
                lokacija.oznaka NOT LIKE 'ODTUJENA' AND
                naprava.rlp LIKE '-'
            ORDER BY
        """ + sortiraj_po + ";"
        tabela_ustreznih = list()
        for inventarna, naziv, tip, serijska, serviser, rlp, dobava, lokacija in cur.execute(sql):
            if lokacija == "ODPISANA" or lokacija == "ODTUJENA" or lokacija == "POSTOPEK ODPISA":
                continue
            temp_naprava = {'Inventarna': inventarna, 'Naziv': naziv, 'Tip' : tip, 'Serijska': serijska,
                            'Servis': serviser, 'RLP': rlp, 'Dobava': dobava, 'Lokacija': lokacija}
            tabela_ustreznih.append(temp_naprava)
        return tabela_ustreznih

    @staticmethod
    def vse_odpisane():
        """
        Vrne vse naprave, ki so odpisane, od njih vrne vse ustrezne podatke
        """
        conn.cursor()
        sql = """
            SELECT naprava.inventarna,
                naprava.naziv,
                naprava.tip,
                naprava.serijska,
                naprava.serviser,
                nahajanje.od,
                lokacija.oznaka
            FROM naprava
                JOIN
                nahajanje ON naprava.inventarna = nahajanje.naprava
                JOIN
                lokacija ON lokacija.id = nahajanje.lokacija
            WHERE nahajanje.[do] IS NULL AND 
                lokacija.oznaka LIKE 'ODPISANA';
        """
        tabela_ustreznih = list()
        for inventarna, naziv, tip, serijska, serviser, od, lokacija in conn.execute(sql):
            temp_naprava = {'Inventarna': inventarna, 'Naziv': naziv, 'Tip' : tip,
                            'Serijska': serijska, 'Servis': serviser, 'Datum odpisa': od, 'Lokacija': lokacija}
            tabela_ustreznih.append(temp_naprava)
        return tabela_ustreznih
    
    @staticmethod
    def vse_odtujene():
        """
        Vrne vse naprave, ki so odtujene, od njih vrne vse ustrezne podatke
        """
        conn.cursor()
        sql = """
            SELECT naprava.inventarna,
                naprava.naziv,
                naprava.tip,
                naprava.serijska,
                naprava.serviser,
                nahajanje.od,
                lokacija.oznaka
            FROM naprava
                JOIN
                nahajanje ON naprava.inventarna = nahajanje.naprava
                JOIN
                lokacija ON lokacija.id = nahajanje.lokacija
            WHERE nahajanje.[do] IS NULL AND 
                lokacija.oznaka LIKE 'ODTUJENA';
        """
        tabela_ustreznih = list()
        for inventarna, naziv, tip, serijska, serviser, od, lokacija in conn.execute(sql):
            temp_naprava = {'Inventarna': inventarna, 'Naziv': naziv, 'Tip' : tip, 'Serijska': serijska,
                            'Servis': serviser, 'Datum odtujitve': od, 'Lokacija': lokacija}
            tabela_ustreznih.append(temp_naprava)
        return tabela_ustreznih

    @staticmethod
    def vse_v_postopku_odpisa():
        """
        Vrne vse naprave, ki so odtujene, od njih vrne vse ustrezne podatke
        """
        conn.cursor()
        sql = """
            SELECT naprava.inventarna,
                naprava.naziv,
                naprava.tip,
                naprava.serijska,
                naprava.serviser,
                nahajanje.od,
                lokacija.oznaka
            FROM naprava
                JOIN
                nahajanje ON naprava.inventarna = nahajanje.naprava
                JOIN
                lokacija ON lokacija.id = nahajanje.lokacija
            WHERE nahajanje.[do] IS NULL AND 
                lokacija.oznaka LIKE 'POSTOPEK ODPISA';
        """
        tabela_ustreznih = list()
        st = 1
        for inventarna, naziv, tip, serijska, serviser, od, lokacija in conn.execute(sql):
            temp_naprava = {'Inventarna': inventarna, 'Naziv': naziv, 'Tip' : tip, 'Serijska': serijska,
                            'Servis': serviser, 'Datum_postopka': od, 'Lokacija': lokacija, 'zap_st': st}
            st += 1
            tabela_ustreznih.append(temp_naprava)
        return tabela_ustreznih

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
        return rez[0] if rez != None else -1

    @staticmethod
    def vrni_aktivacijske_podatke(inventarna):
        """
        Vrne naziv, lokacijo in servis
        """
        cur = conn.cursor()
        sql = """
            SELECT naprava.naziv,
                lokacija.oznaka,
                naprava.serviser
            FROM naprava
                JOIN
                nahajanje ON naprava.inventarna = nahajanje.naprava
                JOIN
                lokacija ON nahajanje.lokacija = lokacija.id
            WHERE inventarna = ?;
        """
        cur.execute(sql, [inventarna])
        rez = cur.fetchone()
        return rez

    def dodaj_v_bazo(self):
        """
        Doda napravo v bazo
        """
        insert = naprava.dodajanje(["inventarna", "naziv", "tip", "garancija", "proizvajalec", 
                                   "serijska", "dobavitelj", "dobava", "serviser", "stroskovno", "rlp"])
        with conn:
            stroskovno_mesto.dodaj_vrstico([self.stroskovno])
            naprava.dodaj_vrstico([self.inventarna, self.naziv, self.tip, self.garancija, self.proizvajalec,
                                  self.serijska, self.dobavitelj, self.dobava, self.serviser, self.stroskovno, self.rlp], insert)

class Popravilo:
    """
    Razred za popravilo
    """
    def __init__(self, st_narocila, tip, opis, opombe, naprava):
        """
        Konstruktor popravila
        """
        self.st_narocila = st_narocila
        self.tip = tip
        self.opis = opis
        self.opombe = opombe
        self.naprava = naprava

    @staticmethod
    def dodaj_opombo(st_narocila, opomba):
        """
        Doda tekst opombe v popravilo z danim st narocila
        """
        cur = conn.cursor()
        sql = """
            UPDATE popravilo
            SET opombe = ?
            WHERE st_narocila = ?;
        """
        cur.execute(sql, [opomba, st_narocila])


    @staticmethod
    def vrni_popravila(inventarna):
        """
        Vrne vsa popravila naprave z inventarno za opis naprave
        """
        sql = """
            SELECT popravilo.st_narocila,
                popravilo.tip,
                popravilo.opis,
                popravilo.opombe,
                faza.datum as aktivacija
            FROM popravilo
                JOIN 
                faza ON popravilo.st_narocila = faza.popravilo
            WHERE popravilo.naprava = ? AND faza.stopnja = 'aktivacija'
            ORDER BY substr(aktivacija, 7) || substr(aktivacija, 4, 2) || substr(aktivacija, 1, 2) DESC
        """
        for st_narocila, tip, opis, opombe, aktivacija in conn.execute(sql, [inventarna]):
            yield {'tip': tip, 'opis': opis if opis != None else "", 'aktivacija': aktivacija,
            'sprejem': Faza.datum_stopnje('sprejem', st_narocila),
            'vrnitev': Faza.datum_stopnje('vrnitev', st_narocila),
            'opombe': opombe if opombe!= None else ''}
    
    def dodaj_v_bazo(self):
        insert = popravilo.dodajanje(["st_narocila", "tip", "opis", "opombe", "naprava"])
        with conn:
            popravilo.dodaj_vrstico([self.st_narocila, self.tip, self.opis, self.opombe, self.naprava], insert)

    @staticmethod
    def popravila_v_fazi(inventarna, faza):
        """
        Vrne stevilo in tabelo vseh popravil, ki so v podani fazi
        """
        tabela_popravil = list()
        faze = {'aktivacija':1, 'sprejem': 2, 'vrnitev':3}
        sql = """
            SELECT faza.popravilo
            FROM faza
                JOIN
                popravilo ON faza.popravilo = popravilo.st_narocila
            WHERE popravilo.naprava = ?
            GROUP BY faza.popravilo
            HAVING count(faza.popravilo) = ?;
        """
        for popravilo in conn.execute(sql, [inventarna, faze[faza]]):
            tabela_popravil.append(popravilo[0])
        return (len(tabela_popravil), tabela_popravil)

    @staticmethod
    def vsa_popravila_v_fazi(faza):
        """
        Vrne inventarno, st narocila, tip in pa datum naprav v tej fazi
        """
        faze = {'aktivacija':1, 'sprejem': 2, 'vrnitev':3}
        sql = """
            SELECT popravilo.naprava,
                popravilo.st_narocila,
                popravilo.tip,
                faza.datum
            FROM faza
                JOIN
                popravilo ON faza.popravilo = popravilo.st_narocila
            GROUP BY faza.popravilo
            HAVING count(faza.popravilo) = ?;
        """
        tabela_ustreznih = list()
        for inventarna, st_narocila, tip, datum in conn.execute(sql, [faze[faza]]):
            tabela_ustreznih.append([inventarna, st_narocila, tip, datum])
        return tabela_ustreznih

    @staticmethod
    def zadnji_rlp(inventarna):
        """
        Vrne kdaj je imela inventarna zadnji letni pregled, ce ga se ni imela vrne -1
        """
        cur = conn.cursor()
        sql = """
        SELECT faza.datum
        FROM popravilo
            JOIN
            faza ON popravilo.st_narocila = faza.popravilo
        WHERE (tip = 'RLP' OR 
                tip = 'RLP in popravilo') AND 
            faza.stopnja = 'vrnitev' AND 
            popravilo.naprava = ?
        ORDER BY substr(faza.datum, 7) || substr(faza.datum, 4, 2) || substr(faza.datum, 1, 2) DESC
        LIMIT 1;
        """
        cur.execute(sql, [inventarna])
        rez = cur.fetchone()
        return rez[0] if rez != None else -1

    @staticmethod
    def vrni_popravilo_po_narocilu(st_narocila):
        """
        Vrne inventarno, ki ima doloceno st narocila in v st faze v kateri je
        Ce ne najde opravila vrne -1
        """
        tabela_popravil = list()
        cur = conn.cursor()
        sql = """
        SELECT popravilo.naprava
        FROM faza
            JOIN
            popravilo ON faza.popravilo = popravilo.st_narocila
        WHERE popravilo.st_narocila = ?;
        """
        for popravilo in conn.execute(sql, [st_narocila]):
            tabela_popravil.append(popravilo[0])
        if tabela_popravil == []:
            return -1, -1
        return (tabela_popravil[0], len(tabela_popravil))

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

    @staticmethod
    def zakljuci_nahajanje(inventarna, datum):
        """
        Za napravo zakljuci nahajanje v katerem je trenutno
        """
        cur = conn.cursor()
        sql = """
        UPDATE nahajanje
        SET [do] = ?
        WHERE nahajanje.naprava = ? AND 
            nahajanje.[do] IS NULL;
        """
        cur.execute(sql, [datum, inventarna])
        conn.commit()
        return 0
    
    @staticmethod
    def lokacija_pred_odtujitvijo(inventarna):
        """
        Vrne na kateri lokaciji se je nahajala naprava pred odtujitvijo
        """
        cur = conn.cursor()
        sql = """
        SELECT lokacija.oznaka
        FROM lokacija
            JOIN
            nahajanje ON lokacija.id = nahajanje.lokacija
        WHERE nahajanje.naprava = ? AND 
            nahajanje.[do] IS NOT NULL AND 
            lokacija.oznaka != 'Odtujena'
        ORDER BY substr(nahajanje.od, 7) || substr(nahajanje.od, 4, 2) || substr(nahajanje.od, 1, 2) DESC
        LIMIT 1;
        """
        cur.execute(sql, [inventarna])
        rez = cur.fetchone()
        return rez[0] if rez != None else -1
    
    def dodaj_v_bazo(self):
        """
        Doda to nahajanje in lokacijo v bazo
        """
        insert = nahajanje.dodajanje(["od", "do", "naprava", "lokacija"])
        with conn:
            id_lokacije = lokacija.dodaj_vrstico([self.lokacija], lokacija.dodajanje(["oznaka"]))
            nahajanje.dodaj_vrstico([self.od, self.do, self.naprava, id_lokacije], insert)



class Lokacija:
    """
    Razred za lokacijo
    """
    def __init__(self, oznaka):
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
        return rez[0] if rez != None else -1

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
            if oznaka[0] == "ODTUJENA" or oznaka[0] == "ODPISANA" or oznaka[0] == "POSTOPEK ODPISA":
                continue
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
    
    @staticmethod
    def seznam_vseh():
        """
        Vrne seznam vseh podjetij
        """
        tabela_oseb = list()
        conn.cursor()
        sql = """
            SELECT ime
            FROM oseba
            ORDER BY ime
        """
        for ime in conn.execute(sql):
            tabela_oseb.append(ime[0])
        return tabela_oseb

    @staticmethod
    def ali_ze_obstaja(ime):
        """
        Vrne id osebe ce ze obtaja drugace vrne -1
        """
        cur = conn.cursor()
        sql = """
            SELECT id
            FROM oseba
            WHERE ime = ?
        """
        cur.execute(sql, [ime])
        rez = cur.fetchone()
        return rez[0] if rez != None else -1
    
    def dodaj_v_bazo(self):
        """
        Doda novo osebo v bazo
        """
        insert = oseba.dodajanje(["ime", "telefon", "email"])
        with conn:
            return oseba.dodaj_vrstico([self.ime, self.telefon, self.email], insert)


class Skrbnistvo:
    """
    Razred za skrbnistvo
    """

    def __init__(self, od=None, do=None, skrbnik=None, naprava=None):
        """
        Kostruktor skrbnistva
        """
        self.od = od
        self.do = do
        self.skrbnik = skrbnik
        self.naprava = naprava

    def dodaj_v_bazo(self):
        """
        Doda to skrbnistvo v bazo
        """
        insert = skrbnistvo.dodajanje(["od", "do", "skrbnik", "naprava"])
        with conn:
            return skrbnistvo.dodaj_vrstico([self.od, self.do, self.skrbnik, self.naprava], insert)
    

class Podjetje:
    """
    Razred za podjetje
    """

    def __init__(self, naziv, telefon=None, email=None):
        """
        Konstruktor podjetja
        """
        self.naziv = naziv
        self.telefon = telefon
        self.email = email

    @staticmethod
    def seznam_vseh():
        """
        Vrne seznam vseh podjetij
        """
        tabela_podjetij = list()
        conn.cursor()
        sql = """
            SELECT naziv
            FROM podjetje
            ORDER BY naziv
        """
        for naziv in conn.execute(sql):
            tabela_podjetij.append(naziv[0])
        return tabela_podjetij

    @staticmethod
    def ali_ze_obstaja(naziv):
        """
        Vrne true ce podjetje ze obstaja
        """
        cur = conn.cursor()
        sql = """
            SELECT naziv
            FROM podjetje
            WHERE naziv = ?
        """
        cur.execute(sql, [naziv])
        rez = cur.fetchone()
        return True if rez != None else False

    def dodaj_v_bazo(self):
        """
        Doda novo podjetje v bazo
        """
        insert = podjetje.dodajanje(["naziv", "telefon", "email"])
        with conn:
            return podjetje.dodaj_vrstico([self.naziv, self.telefon, self.email], insert)


class Datum:
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
        if dan != "-":
            niz_dan = dan if int(dan) >= 10 else ('0' + dan)
        else:
            niz_dan = "-"
        if mesec != "-":
            niz_mesec = mesec if int(mesec) >= 10 else ('0' + mesec)
        else:
            niz_mesec = "-"
        return '.'.join([niz_dan, niz_mesec, leto])
    
    @staticmethod
    def pristej_mesece(niz_datum, st_mesecev):
        """
        Datumu, ki je v nizu pristeje mesece
        """
        st_mesecev = int(st_mesecev)
        dan = int(niz_datum[0:2])
        mesec = int(niz_datum[3:5])
        leto = int(niz_datum[6:])
        mesec += st_mesecev % 12
        if mesec > 12:
            leto += mesec // 12
            mesec = mesec % 12
        leto += st_mesecev // 12

        prestopno_leto = ((leto % 4 == 0) and (leto % 100 != 0)) or (leto % 400 == 0)
        st_dni = [31, 29 if prestopno_leto else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if dan > st_dni[mesec - 1]:
            dan = dan % st_dni[mesec - 1]
            mesec += 1
            #mescov ni potrebno ponovno pregledovati saj ima dec 31 dni
        return '.'.join([str(dan) if dan >= 10 else '0' + str(dan), str(mesec) if mesec >= 10 else '0' + str(mesec), str(leto)])

    @staticmethod
    def za_sortiranje(datum):
        """
        Funckija za sortiranje datumov ki so v nizo
        """
        return datum[6:] + datum[3:5] + datum[0:2]

class Stroskovno:
    """
    Razred za stroskovno mesto
    """

    def __init__(self, oznaka):
        """
        Konstruktor za stroskovno mesto
        """
        self.oznaka = oznaka

    @staticmethod
    def seznam_vseh():
        """
        Vrne seznam vseh stroskovnih mest v bazi
        """
        tabela_stroskovnih = list()
        conn.cursor()
        sql = """
            SELECT oznaka
            FROM stroskovno_mesto
            ORDER BY oznaka
        """
        for oznaka in conn.execute(sql):
            tabela_stroskovnih.append(oznaka[0])
        return tabela_stroskovnih

    