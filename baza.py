import csv

class Tabela():

    def __init__(self, conn):
        self.conn = conn
    
    def izbrisi(self):
        """Izbrise trenutno tabelo"""
        self.conn.execute("DROP TABLE IF EXISTS {};".format(self.ime))

    