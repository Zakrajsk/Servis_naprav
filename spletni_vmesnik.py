import bottle




@bottle.get('/')
def zacetna_stran():
    return bottle.template('zacetna_stran.html')



bottle.run(debug=True, reloader=True)