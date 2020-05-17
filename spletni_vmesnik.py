import bottle
from model import Naprava, Popravilo, Nahajanje, Oseba, Datum, Faza, Lokacija, Podjetje, Stroskovno

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
    print(*podatki)

    garancija = Datum.pretvori_v_niz(podatki['dan_garancija'], podatki['mesec_garancija'], podatki['leto_garancija'])
    dobava = Datum.pretvori_v_niz(podatki['dan_dobava'], podatki['mesec_dobava'], podatki['leto_dobava'])

    nova_naprava = Naprava(podatki['inventarna'], podatki['naziv'], podatki['tip'], garancija,
                           podatki['proizvajalec'], podatki['serijska'], podatki['dobavitelj'],
                           dobava, podatki['serviser'], podatki['stroskovno'], podatki['rlp'])

    return bottle.template('zacetna_stran.html')


@bottle.get('/opis-naprave/')
def opis_opreme():
    return bottle.template('opis_naprave.html', inventarna=None)

@bottle.post('/opis-naprave/')
def opis_post():
    inventarna = bottle.request.forms.get('inventarna')
    return bottle.template(
        'opis_naprave.html',
        inventarna=inventarna,
        naprava = Naprava.opis_naprave(inventarna),
        lokacija = Lokacija.zadnja_lokacija(inventarna),
        skrbnik = Oseba.zadnji_skrbnik(inventarna),
        popravila = Popravilo.vrni_popravila(inventarna),
        odtujenosti = Nahajanje.odtujenosti(inventarna))

@bottle.get('/izpisi/')
def izpisi():
    return bottle.template('izpis.html', tip_izpisa=None)

@bottle.post('/izpisi/')
def izpisi_post():
    tip_izpisa = bottle.request.forms.get('tip_izpisa')
    return bottle.template('izpis.html', tip_izpisa=tip_izpisa)

@bottle.get('/aktivacija-postopka/')
def aktiviraj_postopek():
    return bottle.template('aktivacija_postopka.html', inventarna="")

@bottle.post('/aktivacija-postopka/')
def aktiviraj_postopek_post():
    if bottle.request.forms.get('iskanje_naprave'):
        inventarna = bottle.request.forms.get('inventarna')
        return bottle.template(
            'aktivacija_postopka.html',
            inventarna=inventarna,
            naziv = Naprava.vrni_naziv(inventarna),
            lokacija = Lokacija.zadnja_lokacija(inventarna))

    elif bottle.request.forms.get('potrditev_sprememb'):
        podatki = bottle.request.forms
        inventarna = podatki.get('inventarna')
        st_narocila = podatki.get('st_narocila')
        opis_napake = podatki.get('opis_napake')
        tip = podatki.get('tip')
        dan = podatki.get('dan')
        mesec = podatki.get('mesec')
        leto = podatki.get('leto')
        datum = Datum.pretvori_v_niz(dan, mesec, leto)
        popravilo = Popravilo(st_narocila, tip, opis_napake, inventarna)
        faza = Faza('aktivacija', st_narocila, datum)
        popravilo.dodaj_v_bazo()
        faza.dodaj_v_bazo()
        
        return bottle.template('zacetna_stran.html')
    

@bottle.get('/prevzem/')
def prevzem():
    return bottle.template('prevzem.html',
                            inventarna="",
                            napaka="")

@bottle.post('/prevzem/')
def prevzem_post():
    if bottle.request.forms.get('iskanje_naprave'):
        inventarna = bottle.request.forms.get('inventarna')
        st, popravila = Popravilo.popravila_v_fazi(inventarna, 'aktivacija')
        return bottle.template(
            'prevzem.html',
            inventarna=inventarna,
            naziv = Naprava.vrni_naziv(inventarna),
            lokacija = Lokacija.zadnja_lokacija(inventarna),
            napaka = True if st == 0 else False)

    elif bottle.request.forms.get('potrditev_sprememb'):
        podatki = bottle.request.forms
        inventarna = podatki.get('inventarna')
        dan = podatki.get('dan')
        mesec = podatki.get('mesec')
        leto = podatki.get('leto')
        datum = Datum.pretvori_v_niz(dan, mesec, leto)
        st, popravilo = Popravilo.popravila_v_fazi(inventarna, 'aktivacija')
        faza = Faza('sprejem', popravilo[0], datum)
        faza.dodaj_v_bazo()
        return bottle.template('zacetna_stran.html')

@bottle.get('/vrnitev/')
def vrnitev():
    return bottle.template('vrnitev.html',
                            inventarna="",
                            napaka="")

@bottle.post('/vrnitev/')
def vrnitev_post():
    if bottle.request.forms.get('iskanje_naprave'):
        inventarna = bottle.request.forms.get('inventarna')
        st, popravila = Popravilo.popravila_v_fazi(inventarna, 'sprejem')
        return bottle.template(
            'vrnitev.html',
            inventarna=inventarna,
            naziv = Naprava.vrni_naziv(inventarna),
            lokacija = Lokacija.zadnja_lokacija(inventarna),
            napaka = True if st == 0 else False)

    elif bottle.request.forms.get('potrditev_sprememb'):
        podatki = bottle.request.forms
        inventarna = podatki.get('inventarna')
        dan = podatki.get('dan')
        mesec = podatki.get('mesec')
        leto = podatki.get('leto')
        datum = Datum.pretvori_v_niz(dan, mesec, leto)
        st, popravilo = Popravilo.popravila_v_fazi(inventarna, 'sprejem')
        faza = Faza('vrnitev', popravilo[0], datum)
        faza.dodaj_v_bazo()
        if podatki.get('zakljucitev'):
            koncna_faza = Faza('zakljuceno', popravilo[0])
            koncna_faza.dodaj_v_bazo()
        return bottle.template('zacetna_stran.html')

@bottle.get('/zakljucek/')
def zakljuci():
    return bottle.template('zakljuci.html',
                            inventarna="",
                            napaka="")

@bottle.post('/zakljucek/')
def zakluci_post():
    if bottle.request.forms.get('iskanje_naprave'):
        inventarna = bottle.request.forms.get('inventarna')
        st, popravila = Popravilo.popravila_v_fazi(inventarna, 'vrnitev')
        return bottle.template(
            'zakljuci.html',
            inventarna=inventarna,
            naziv = Naprava.vrni_naziv(inventarna),
            lokacija = Lokacija.zadnja_lokacija(inventarna),
            napaka = True if st == 0 else False)

    elif bottle.request.forms.get('potrditev_sprememb'):
        podatki = bottle.request.forms
        inventarna = podatki.get('inventarna')
        st, popravilo = Popravilo.popravila_v_fazi(inventarna, 'vrnitev')
        faza = Faza('zakljuceno', popravilo[0])
        faza.dodaj_v_bazo()
        return bottle.template('zacetna_stran.html')

@bottle.get('/aktivirane-naprave/')
def aktivirane_naprave():
    return bottle.template('aktivirane_naprave.html')

@bottle.get('/na-servisu/')
def na_servisu():
    return bottle.template('na_servisu.html')

@bottle.get('/nedokoncani/')
def nedokoncani():
    return bottle.template('nedokoncani.html')

@bottle.get('/odtujen/')
def odtujen():
    return bottle.template('odtujen.html', inventarna=None)

@bottle.post('/odtujen/')
def odtujen_post():
    inventarna = bottle.request.forms.get('inventarna')
    return bottle.template('odtujen.html', inventarna=inventarna)

@bottle.get('/odpis/')
def odpis():
    return bottle.template('odpis.html', inventarna=None)

@bottle.post('/odpis/')
def odpis_post():
    inventarna = bottle.request.forms.get('inventarna')
    return bottle.template('odpis.html', inventarna=inventarna)


bottle.run(debug=True, reloader=True)