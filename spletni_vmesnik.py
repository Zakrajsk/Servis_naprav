import bottle
from model import Naprava, Popravilo, Nahajanje, Oseba

bottle.TEMPLATE_PATH.insert(0,'views')


@bottle.get('/')
def zacetna_stran():
    return bottle.template('zacetna_stran.html')

@bottle.get('/nova-oprema/')
def nova_naprava():
    return bottle.template('nova_oprema.html')

@bottle.get('/opis-naprave/')
def opis_opreme():
    return bottle.template('opis_naprave.html', inventarna=None)

@bottle.post('/opis-naprave/')
def opis_post():
    inventarna = bottle.request.forms['inventarna']
    return bottle.template(
        'opis_naprave.html',
        inventarna=inventarna,
        naprava = Naprava.opis_naprave(inventarna),
        lokacija = Nahajanje.zadnja_lokacija(inventarna),
        skrbnik = Oseba.zadnji_skrbnik(inventarna),
        popravila = Popravilo.vrni_popravila(inventarna),
        odtujenosti = Nahajanje.odtujenosti(inventarna))

@bottle.get('/izpisi/')
def izpisi():
    return bottle.template('izpis.html', tip_izpisa=None)

@bottle.post('/izpisi/')
def izpisi_post():
    tip_izpisa = bottle.request.forms['tip_izpisa']
    return bottle.template('izpis.html', tip_izpisa=tip_izpisa)

@bottle.get('/aktivacija-postopka/')
def aktiviraj_postopek():
    return bottle.template('aktivacija_postopka.html', inventarna=None)

@bottle.post('/aktivacija-postopka/')
def aktiviraj_postopek_post():
    inventarna = bottle.request.forms['inventarna']
    return bottle.template(
        'aktivacija_postopka.html',
        inventarna=inventarna,
        naziv = Naprava.vrni_naziv(inventarna),
        lokacija = Nahajanje.zadnja_lokacija(inventarna))

@bottle.get('/prevzem/')
def prevzem():
    return bottle.template('prevzem.html', inventarna=None)

@bottle.post('/prevzem/')
def prevzem_post():
    inventarna = bottle.request.forms['inventarna']
    return bottle.template('prevzem.html', inventarna=inventarna)

@bottle.get('/vrnitev/')
def vrnitev():
    return bottle.template('vrnitev.html', inventarna=None)

@bottle.post('/vrnitev/')
def vrnitev_post():
    inventarna = bottle.request.forms['inventarna']
    return bottle.template('vrnitev.html', inventarna=inventarna)

@bottle.get('/zakljucek/')
def zakljuci():
    return bottle.template('zakljuci.html', inventarna=None)

@bottle.post('/zakljucek/')
def zakluci_post():
    inventarna = bottle.request.forms['inventarna']
    return bottle.template('zakljuci.html', inventarna=inventarna)

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
    inventarna = bottle.request.forms['inventarna']
    return bottle.template('odtujen.html', inventarna=inventarna)

@bottle.get('/odpis/')
def odpis():
    return bottle.template('odpis.html', inventarna=None)

@bottle.post('/odpis/')
def odpis_post():
    inventarna = bottle.request.forms['inventarna']
    return bottle.template('odpis.html', inventarna=inventarna)


bottle.run(debug=True, reloader=True)