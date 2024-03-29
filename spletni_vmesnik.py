import bottle
from model import Naprava, Popravilo, Nahajanje, Oseba, Datum, Faza, Lokacija, Podjetje, Stroskovno, Skrbnistvo

bottle.TEMPLATE_PATH.insert(0,'views')


@bottle.get('/')
def zacetna_stran():
    return bottle.template('zacetna_stran.html')

@bottle.get('/nova-oprema/')
def nova_naprava():
    return bottle.template('nova_oprema.html',
                            lokacije = Lokacija.seznam_lokacij(),
                            podjetja = Podjetje.seznam_vseh(),
                            stroskovna = Stroskovno.seznam_vseh(),
                            osebe = Oseba.seznam_vseh())

@bottle.post('/nova-oprema/')
def nova_naprava_post():
    podatki = bottle.request.forms
    print(podatki.skrbnik)
    celotna_inventarna = "74600" + podatki['inventarna']

    garancija = Datum.pretvori_v_niz(podatki['dan_garancija'], podatki['mesec_garancija'], podatki['leto_garancija'])
    dobava = Datum.pretvori_v_niz(podatki['dan_dobava'], podatki['mesec_dobava'], podatki['leto_dobava'])

    #ali obstaja ta dobavitelj
    if not Podjetje.ali_ze_obstaja(podatki["dobavitelj"]):
        print("dobavitelj se ne obstaja")
        nov_dobavitelj = Podjetje(podatki['dobavitelj'], podatki['telefon_dobavitelj'], podatki['email_dobavitelj'])
        nov_dobavitelj.dodaj_v_bazo()

    if not Podjetje.ali_ze_obstaja(podatki["serviser"]):
        print("serviser se ne obstaja")
        nov_serviser = Podjetje(podatki['serviser'], podatki['telefon_serviser'], podatki['email_serviser'])
        nov_serviser.dodaj_v_bazo()

    nova_naprava = Naprava(celotna_inventarna, podatki['naziv'], podatki['tip'], garancija,
                           podatki['proizvajalec'], podatki['serijska'], podatki['dobavitelj'],
                           dobava, podatki['serviser'], podatki['stroskovno'], podatki['RLP'])
    novo_nahajanje = Nahajanje(od=dobava, naprava=celotna_inventarna, lokacija=podatki['lokacija'])

    nova_naprava.dodaj_v_bazo()
    novo_nahajanje.dodaj_v_bazo()

    id_skrbnika = Oseba.ali_ze_obstaja(podatki["skrbnik"])
    #ali obstaja ta skrbnik
    if id_skrbnika == -1:
        #dodamo osebo, ker je nova
        nov_skrbnik = Oseba(podatki["skrbnik"], podatki["telefon_skrbnik"], podatki["email_skrbnik"])
        id_skrbnika = nov_skrbnik.dodaj_v_bazo()

    novo_skrbnistvo = Skrbnistvo(od=dobava, skrbnik=id_skrbnika, naprava=celotna_inventarna)
    novo_skrbnistvo.dodaj_v_bazo()
    
    return bottle.template('zacetna_stran.html')


@bottle.get('/opis-naprave/')
def opis_opreme():
    return bottle.template('opis_naprave.html', inventarna="", napaka="")

@bottle.post('/opis-naprave/')
def opis_post():
    inventarna = bottle.request.forms.get('inventarna')
    cela_inventarna = "74600" + inventarna
    napaka = False
    naprava = Naprava.opis_naprave(cela_inventarna)
    lokacija = ""
    skrbnik = ""
    popravila = []
    odtujenosti = []
    if naprava == None:
        napaka = "Inventarna številka ne obstaja"
    else:
        lokacija = Lokacija.zadnja_lokacija(cela_inventarna)
        skrbnik = Oseba.zadnji_skrbnik(cela_inventarna)
        popravila = Popravilo.vrni_popravila(cela_inventarna)
        odtujenosti = Nahajanje.odtujenosti(cela_inventarna)
    return bottle.template(
        'opis_naprave.html',
        inventarna=inventarna,
        naprava = naprava,
        lokacija = lokacija,
        skrbnik = skrbnik,
        popravila = popravila,
        odtujenosti = odtujenosti,
        napaka = napaka)

@bottle.get('/izpisi/')
def izpisi():
    return bottle.template('izpis.html', tip_izpisa=None)

@bottle.post('/izpisi/')
def izpisi_post():
    tip_izpisa = bottle.request.forms.get('tip_izpisa')
    if tip_izpisa == None:
        return bottle.template('izpis.html', tip_izpisa=None)
    vrstni_red_stolpcev = list()
    tabela_moznih_stolpcev = ['Inventarna', 'Naziv', 'Tip', 'Serijska', 'Servis', 'Lokacija', 'Naslednji RLP',
                              'Datum odpisa', 'Datum odtujitve']
    
    zaporedja = {'lokacije': '501234', 'serviserji': '401235', 'RLP': '6012354', 'odpisani': '7012354',
                 'odtujeni': '8012354', 'nazivi': '102354', 'brez_RLP': '102354'}

    slovar_sortiranja = {'lokacije': 'lokacija.oznaka', 'serviserji': 'naprava.serviser', 'nazivi': 'naprava.naziv', 'RLP': 'naprava.naziv'}

    if tip_izpisa not in ['odpisani', 'odtujeni', "RLP", "brez_RLP"]:
        tabela_vseh_naprav = Naprava.vse_za_izpis(slovar_sortiranja[tip_izpisa])
    elif tip_izpisa == 'RLP':
        tabela_vseh_naprav = Naprava.vse_za_rlp_izpis(slovar_sortiranja[tip_izpisa])
    elif tip_izpisa == "brez_RLP":
        tabela_vseh_naprav = Naprava.vse_brez_rlp_izpis(slovar_sortiranja['RLP'])
    elif tip_izpisa == 'odpisani':
        tabela_vseh_naprav = Naprava.vse_odpisane()
    else:
        tabela_vseh_naprav = Naprava.vse_odtujene()
    
    for stolpec in zaporedja[tip_izpisa]:
        vrstni_red_stolpcev.append(tabela_moznih_stolpcev[int(stolpec)])

    if tip_izpisa == 'RLP':
        st = 0
        #za vse naprave zracunamo naslednji datum letnega pregleda
        for naprava in tabela_vseh_naprav:
            datum_zadnjega_RLP = Popravilo.zadnji_rlp(naprava['Inventarna'])
            if datum_zadnjega_RLP == -1:
                if '-' in naprava['Dobava']:
                    naprava['Naslednji RLP'] = "Se_ne_da " + naprava['Dobava']
                else:
                    naprava['Naslednji RLP'] = Datum.pristej_mesece(naprava['Dobava'], naprava['RLP'])
            else:
                nov_datum = Datum.pristej_mesece(datum_zadnjega_RLP, naprava['RLP'])
                naprava['Naslednji RLP'] = nov_datum
        tabela_vseh_naprav.sort(key=lambda x: Datum.za_sortiranje(x['Naslednji RLP']))
                
    return bottle.template('izpis.html', tip_izpisa=tip_izpisa, stolpci=vrstni_red_stolpcev, vse_naprave = tabela_vseh_naprav)


@bottle.get('/sprememba-podatka/')
def sprememba_podatka():
    return bottle.template('sprememba_podatka.html', inventarna="", napaka="", tip_spremembe=False)

@bottle.post('/sprememba-podatka/')
def sprememba_podatka_post():
    if bottle.request.forms.get('iskanje_naprave'):
        inventarna = bottle.request.forms.get('inventarna')
        izbrano = bottle.request.forms.get('katera_sprememba')
        napaka = False
        podatki = {'tabela' : [], 'lokacija': ""}
        izbran_tip = False
        tip_spremembe = {'naziv': 1, 'tip': 1, 'serijska': 1, 'lokacija': 6, 'stroskovno': 2,
                        'skrbnik': 3, 'proizvajalec': 1, 'dobavitelj': 3, 'serviser': 3, 'RLP': 5,
                        'garancija': 4, 'dobava': 4 }
        if izbrano == None:
            napaka = "Ni izbrano kaj želiš spreminjati!"
        else:
            izbran_tip = tip_spremembe[izbrano]
        cela_inventarna = "74600" + inventarna

        naziv = Naprava.vrni_naziv(cela_inventarna)
        if naziv == -1:
            napaka = "Naprava z to inventarno ne obstaja"
            naziv = "Preveri inventarno"

        if izbrano == "lokacija":
            podatki['lokacija'] = Lokacija.zadnja_lokacija(cela_inventarna)
            podatki['tabela'] = Lokacija.seznam_lokacij()
        
        return bottle.template('sprememba_podatka.html',
                                inventarna=inventarna,
                                naziv = naziv,
                                napaka = napaka,
                                tip_spremembe=izbran_tip,
                                podatki = podatki)

    elif bottle.request.forms.get('potrditev_sprememb'):
        return bottle.template('zacetna_stran.html')



@bottle.get('/aktivacija-postopka/')
def aktiviraj_postopek():
    return bottle.template('aktivacija_postopka.html',
                            inventarna="",
                            napaka="")

@bottle.post('/aktivacija-postopka/')
def aktiviraj_postopek_post():
    if bottle.request.forms.get('iskanje_naprave'):
        napaka = False
        inventarna = bottle.request.forms.get('inventarna')
        cela_inventarna = "74600" + inventarna
        naziv = Naprava.vrni_naziv(cela_inventarna)
        lokacija = Lokacija.zadnja_lokacija(cela_inventarna)
        if naziv == -1:
            napaka = "Naprave ni mogoče najti"
            naziv = "Preveri vnešeno inventarno številko"
            lokacija = "Preveri vnešeno inventarno številko"
        return bottle.template(
            'aktivacija_postopka.html',
            inventarna = inventarna,
            naziv = naziv,
            lokacija = lokacija,
            napaka = napaka)

    elif bottle.request.forms.get('potrditev_sprememb'):
        podatki = bottle.request.forms
        inventarna = podatki.get('inventarna')
        cela_inventarna = "74600" + inventarna
        st_narocila = podatki.get('st_narocila')
        opis_napake = podatki.get('opis_napake')
        tip = podatki.get('tip')
        dan = podatki.get('dan')
        mesec = podatki.get('mesec')
        leto = podatki.get('leto')
        datum = Datum.pretvori_v_niz(dan, mesec, leto)
        popravilo = Popravilo(st_narocila, tip, opis_napake, None, cela_inventarna)
        faza = Faza('aktivacija', st_narocila, datum)
        popravilo.dodaj_v_bazo()
        faza.dodaj_v_bazo()
        
        return bottle.template('zacetna_stran.html')
    

@bottle.get('/prevzem/')
def prevzem():
    return bottle.template('prevzem.html',
                            st_narocila="",
                            napaka="")

@bottle.post('/prevzem/')
def prevzem_post():
    if bottle.request.forms.get('iskanje_naprave'):
        napaka = False
        st_narocila = bottle.request.forms.get('st_narocila')
        #st, popravila = Popravilo.popravila_v_fazi(inventarna, 'aktivacija')
        inventarna, st_faze = Popravilo.vrni_popravilo_po_narocilu(st_narocila)
        naziv = "Preveri vnešeno naročilo"
        lokacija = "Preveri vnešeno naročilo"
        if inventarna == -1 or st_faze <= 0:
            napaka = "Za to naročilo še ni bila vnešena aktivacija postopka ali pa je napačno vnešena številka naročila."
            
        elif st_faze > 1:
            napaka = "Za to narocilo je že bil vnešen prevzem."

        else:
            naziv = Naprava.vrni_naziv(inventarna)
            lokacija = Lokacija.zadnja_lokacija(inventarna)

        return bottle.template(
            'prevzem.html',
            st_narocila = st_narocila,
            naziv = naziv,
            lokacija = lokacija,
            napaka = napaka)

    elif bottle.request.forms.get('potrditev_sprememb'):
        podatki = bottle.request.forms
        st_narocila = podatki.get('st_narocila')
        dan = podatki.get('dan')
        mesec = podatki.get('mesec')
        leto = podatki.get('leto')
        datum = Datum.pretvori_v_niz(dan, mesec, leto)
        #st, popravilo = Popravilo.popravila_v_fazi(inventarna, 'aktivacija')
        faza = Faza('sprejem', st_narocila, datum)
        faza.dodaj_v_bazo()
        return bottle.template('zacetna_stran.html')

@bottle.get('/vrnitev/')
def vrnitev():
    return bottle.template('vrnitev.html',
                            st_narocila="",
                            napaka="")

@bottle.post('/vrnitev/')
def vrnitev_post():
    if bottle.request.forms.get('iskanje_naprave'):
        napaka = False
        st_narocila = bottle.request.forms.get('st_narocila')
        #st, popravila = Popravilo.popravila_v_fazi(inventarna, 'sprejem')
        inventarna, st_faze = Popravilo.vrni_popravilo_po_narocilu(st_narocila)
        naziv = "Preveri vnešeno naročilo"
        lokacija = "Preveri vnešeno naročilo"
        if inventarna == -1 or st_faze <= 1:
            napaka = "Za to naročilo še ni bil vnešen prevzem ali pa je napačno vnešena številka naročila."
            
        elif st_faze > 2:
            napaka = "Za to narocilo je že bila vnešena vrnitev."

        else:
            naziv = Naprava.vrni_naziv(inventarna)
            lokacija = Lokacija.zadnja_lokacija(inventarna)

        return bottle.template(
            'vrnitev.html',
            st_narocila=st_narocila,
            naziv = naziv,
            lokacija = lokacija,
            napaka = napaka)

    elif bottle.request.forms.get('potrditev_sprememb'):
        podatki = bottle.request.forms
        st_narocila = podatki.get('st_narocila')
        dan = podatki.get('dan')
        mesec = podatki.get('mesec')
        leto = podatki.get('leto')
        opomba = podatki.get('opomba')
        datum = Datum.pretvori_v_niz(dan, mesec, leto)
        #st, popravilo = Popravilo.popravila_v_fazi(inventarna, 'sprejem')
        faza = Faza('vrnitev', st_narocila, datum)
        faza.dodaj_v_bazo()
        Popravilo.dodaj_opombo(st_narocila, opomba)
        if podatki.get('zakljucitev'):
            koncna_faza = Faza('zakljuceno', st_narocila)
            koncna_faza.dodaj_v_bazo()
        return bottle.template('zacetna_stran.html')

@bottle.get('/zakljucek/')
def zakljuci():
    return bottle.template('zakljuci.html',
                            st_narocila="",
                            napaka="")

@bottle.post('/zakljucek/')
def zakluci_post():
    if bottle.request.forms.get('iskanje_naprave'):
        napaka = False
        st_narocila = bottle.request.forms.get('st_narocila')
        #st, popravila = Popravilo.popravila_v_fazi(inventarna, 'vrnitev')
        inventarna, st_faze = Popravilo.vrni_popravilo_po_narocilu(st_narocila)
        naziv = "Preveri vnešeno naročilo"
        lokacija = "Preveri vnešeno naročilo"
        if inventarna == -1 or st_faze <= 2:
            napaka = "Za to naročilo še ni bila vnešena vrnitev ali pa je napačna številka naročila."
            
        elif st_faze > 3:
            napaka = "To naročilo je že zaključeno ."

        else:
            naziv = Naprava.vrni_naziv(inventarna)
            lokacija = Lokacija.zadnja_lokacija(inventarna)

        return bottle.template(
            'zakljuci.html',
            st_narocila=st_narocila,
            naziv = naziv,
            lokacija = lokacija,
            napaka = napaka)

    elif bottle.request.forms.get('potrditev_sprememb'):
        podatki = bottle.request.forms
        st_narocila = podatki.get('st_narocila')
        #st, popravilo = Popravilo.popravila_v_fazi(inventarna, 'vrnitev')
        faza = Faza('zakljuceno', st_narocila)
        faza.dodaj_v_bazo()
        return bottle.template('zacetna_stran.html')

@bottle.get('/aktivirane-naprave/')
def aktivirane_naprave():
    vse_naprave_v_aktivaciji = Popravilo.vsa_popravila_v_fazi('aktivacija')
    koncna_tabela = list()
    for st, posamezna in enumerate(vse_naprave_v_aktivaciji):
        temp = list(Naprava.vrni_aktivacijske_podatke(posamezna[0]))
        koncna_tabela.append([st + 1, posamezna[0]] + [temp[0]] + posamezna[1:] + temp[1:])
    return bottle.template('aktivirane_naprave.html', vse_naprave=koncna_tabela)

@bottle.get('/na-servisu/')
def na_servisu():
    vse_naprave_v_prevzemu = Popravilo.vsa_popravila_v_fazi('sprejem')
    koncna_tabela = list()
    for st, posamezna in enumerate(vse_naprave_v_prevzemu):
        temp = list(Naprava.vrni_aktivacijske_podatke(posamezna[0]))
        koncna_tabela.append([st + 1, posamezna[0]] + [temp[0]] + posamezna[2:] + temp[1:])
    return bottle.template('na_servisu.html', vse_naprave=koncna_tabela)

@bottle.get('/nedokoncani/')
def nedokoncani():
    vse_naprave_nedokoncane = Popravilo.vsa_popravila_v_fazi('vrnitev')
    koncna_tabela = list()
    for st, posamezna in enumerate(vse_naprave_nedokoncane):
        temp = list(Naprava.vrni_aktivacijske_podatke(posamezna[0]))
        koncna_tabela.append([st + 1, posamezna[0]] + [temp[0]] + posamezna[2:] + temp[1:])
    return bottle.template('nedokoncani.html', vse_naprave=koncna_tabela)

@bottle.get('/odtujen/')
def odtujen():
    return bottle.template('odtujen.html', inventarna="", napaka="", izbrana=None)

@bottle.post('/odtujen/')
def odtujen_post():
    inventarna = bottle.request.forms.get('inventarna')
    
    if bottle.request.forms.get('iskanje_naprave'):
        inventarna = bottle.request.forms.get('inventarna')
        cela_inventarna = "74600" + inventarna
        odtujitev = bottle.request.forms.get('Odtujitev_vrnitev')
        trenutna_lokacija = Lokacija.zadnja_lokacija(cela_inventarna)
        napaka = False
        if odtujitev == None:
            napaka = "Ni bilo izbrano ali je odtujitev ali vrnitev"
        if odtujitev == 'ODT':
            #naprava je bila odtujena
            if trenutna_lokacija == 'ODTUJENA':
                #naprava je ze odtujena, zato vrnemo napako
                napaka = "Naprava je že zabeležena kot odtujena"
        if odtujitev == 'VRN':
            #naprava je bila najdena
            if trenutna_lokacija != 'ODTUJENA':
                #ce ni odtujena potem ne more biti najdena
                napaka = "Naprava ni odtujena"
        
        naziv = Naprava.vrni_naziv(cela_inventarna)
        if naziv == -1:
            napaka = "Inventarna številka ne obstaja"
            naziv = "Preveri inventarno številko"
            trenutna_lokacija = "Preveri inventarno številko"

        return bottle.template(
            'odtujen.html',
            inventarna=inventarna,
            naziv = naziv,
            lokacija = trenutna_lokacija,
            napaka = napaka,
            izbrana = odtujitev)

    elif bottle.request.forms.get('potrditev_sprememb'):
        podatki = bottle.request.forms
        inventarna = "74600" + podatki.get('inventarna')
        dan = podatki.get('dan')
        mesec = podatki.get('mesec')
        leto = podatki.get('leto')
        odtujitev = podatki.get('Odtujitev_vrnitev')
        datum = Datum.pretvori_v_niz(dan, mesec, leto)
        
        if odtujitev == 'ODT':
            #napravo bomo dali kot odtujeno
            Nahajanje.zakljuci_nahajanje(inventarna, datum)
            novo_nahajanje = Nahajanje(datum, naprava=inventarna, lokacija='ODTUJENA')
        else:
            #napravo damo kot vrnjeno in jo postavimo na prejsno lokacijo
            prejsna_lokacija = Nahajanje.lokacija_pred_odtujitvijo(inventarna)
            print(prejsna_lokacija)
            Nahajanje.zakljuci_nahajanje(inventarna, datum)
            novo_nahajanje = Nahajanje(datum, naprava=inventarna, lokacija=prejsna_lokacija)
        novo_nahajanje.dodaj_v_bazo()
        return bottle.template('zacetna_stran.html')

@bottle.get('/postopek-odpisa/')
def postopek_odpisa():
    vse_naprave_v_postopku_odpisa = Naprava.vse_v_postopku_odpisa()
    return bottle.template('postopek_odpisa.html', vse_naprave=vse_naprave_v_postopku_odpisa)


@bottle.get('/odpis/')
def odpis():
    return bottle.template('odpis.html', inventarna="", napaka="", izbrana=None)

@bottle.post('/odpis/')
def odpis_post():
    inventarna = bottle.request.forms.get('inventarna')
    cela_inventarna = "74600" + inventarna
    if bottle.request.forms.get('iskanje_naprave'):
        vrsta_vnosa = bottle.request.forms.get('zacni_koncaj')
        trenutna_lokacija = Lokacija.zadnja_lokacija(cela_inventarna)
        napaka = False
        if vrsta_vnosa == None:
            napaka = "Ni bilo izbrano ali se začne postopek ali dokončen odpis "
        if vrsta_vnosa == 'ZAC':
            #naprava je bila odtujena
            if trenutna_lokacija == 'POSTOPEK ODPISA':
                #naprava je ze odtujena, zato vrnemo napako
                napaka = "Naprava je že v postopku odpisa"
        if vrsta_vnosa == 'KON':
            #naprava je bila dokoncno odpisana
            if trenutna_lokacija != 'POSTOPEK ODPISA':
                #Naprava se ni bila v postopku odpisa
                napaka = "Za napravo se ni bil aktiviran postopek odpisa"
        naziv = Naprava.vrni_naziv(cela_inventarna)
        if naziv == -1:
            napaka = "Inventarna številka ne obstaja"
            naziv = "Preveri inventarno številko"
            trenutna_lokacija = "Preveri inventarno številko"

        return bottle.template(
            'odpis.html',
            inventarna=inventarna,
            naziv = naziv,
            lokacija = trenutna_lokacija,
            napaka = napaka,
            izbrana = vrsta_vnosa)

    elif bottle.request.forms.get('potrditev_sprememb'):
        podatki = bottle.request.forms
        inventarna = podatki.get('inventarna')
        cela_inventarna = "74600" + inventarna
        dan = podatki.get('dan')
        mesec = podatki.get('mesec')
        leto = podatki.get('leto')
        odtujitev = podatki.get('zacni_koncaj')
        datum = Datum.pretvori_v_niz(dan, mesec, leto)
        
        if odtujitev == 'ZAC':
            #napravo bomo dali v postopek odtujitve
            Nahajanje.zakljuci_nahajanje(cela_inventarna, datum)
            novo_nahajanje = Nahajanje(datum, naprava=cela_inventarna, lokacija="POSTOPEK ODPISA")
        else:
            #napravo damo kot odpisano
            Nahajanje.zakljuci_nahajanje(cela_inventarna, datum)
            novo_nahajanje = Nahajanje(datum, naprava=cela_inventarna, lokacija="ODPISANA")
        novo_nahajanje.dodaj_v_bazo()
        return bottle.template('zacetna_stran.html')


bottle.run(debug=True, reloader=True)