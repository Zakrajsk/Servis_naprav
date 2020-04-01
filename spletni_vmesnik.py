import bottle

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
    return bottle.template('opis_naprave.html', inventarna=inventarna)

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
    return bottle.template('aktivacija_postopka.html', inventarna=inventarna)



bottle.run(debug=True, reloader=True)