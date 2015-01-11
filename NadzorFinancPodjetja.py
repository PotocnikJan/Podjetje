from Bottle import *
import sqlite3
datoteka_baze = "Podjetje.sqlite"
baza = sqlite3.connect(datoteka_baze,isolation_level=None)

def izracunajPromet():
    #Za začetek izračunajmo dosedanji promet podjetja
    ''' Vrne dosedanji promet podjetja.'''
    with baza:
        baza.execute("""SELECT SUM(cena) FROM racuni""")
        return baza.fetchone()   

def izracunajStroski():
    ''' Vrne dosedanje stroške podjetja.'''
    with baza:
        baza.execute("""SELECT SUM(cena) FROM stroski""")
        return baza.fetchone()
    
def zasluzek():
    '''Funkcija vrne zaslužek podjetja, ki predstavlja razliko med prometom in stroški.'''
    return (izracunajPromet() - izracunajSroski())

def prometOdStranke(stranka):
    #join glede na tabeli stranke in izdani racuni.
    '''Vrne promet, ki ga je podjetje imelo od določene stranke.'''
    with baza:
        baza.execute('''SELECT racuni.id,racuni.cena,racuni.datum
                        FROM racuni
                        JOIN stranke ON stranke.id = racuni.id_stranke
                        WHERE ime LIKE ?%''',[stranka])
        return baza.fetchall()
                         
def prometObdobje(datum1,datum2):
    '''Vrne količino prometa,ki ga je podjetje ustvarilo v določenem časovnem intervalu'''
    with baza:
        baza.execute('''SELECT sum(cena) FROM racuni WHERE datum IS BETWEEN ? AND ?''',[datum1,datum2])
                                             
def izdaniRacuni(datum):
    '''Vrne vse izdane račune od določenega datuma naprej in jih poveže s strankami'''
    with baza:
        baza.execute('''SELECT racuni.id,racuni.cena,racuni.datum
                        FROM racuni
                        JOIN stranke ON stranke.id = racuni.id_stranke
                        WHERE datum > ?%''',[datum])
        return baza.fetchall()
def dodajRacun(ime_stranke,cena,ddv,datum):
    '''V bazo dodamo nov račun'''   
    
    def dobiIDstranke(ime_stranke):
        with baza:
            baza.execute('SELECT id_stranke FROM stranke WHERE ime_stranke = ime')
            return baza.fetchone()
    id_stranke = dobiIDstranke(ime_stranke)
    c = baza.cursor()
    c.execute('''INSERT INTO racuni (id_stranke, cena, ddv, datum) VALUES (?, ?)''', [id_stranke, cena, ddv, datum])
    c.close()
    id_racuna = c.lastrowid 
    return id_racuna

def dodaj_strosek(vrsta_stroska, cena, ddv, datum):

    '''V bazo dodamo uporabnika: njegovo uporabniško ime in zakodirano geslo'''
    c = baza.cursor()
    c.execute('''INSERT INTO stroski (vrsta_stroska, cena, ddv, datum) VALUES (?, ?, ?, ?)''', [vrsta_stroska, cena, ddv, datum])
    c.close()
    id_stroska = c.lastrowid 
    return id_stroska
###########################################################################################################
#Spodaj se nahajajo funkcije, ki poskrbijo, da lahko preverjamo pristnost uporabnikov, ter po možnosti v bazo dodajamo
#nove uporabnike.
def zakodiraj(geslo):
    return hashlib.md5(geslo.encode()).hexdigest()

def dodaj_uporabnika(up_ime, geslo):

    '''V bazo dodamo uporabnika: njegovo uporabniško ime in zakodirano geslo'''
    c = baza.cursor()
    c.execute('''INSERT INTO uporabniki (up_ime, geslo) VALUES (?, ?)''', [up_ime, zakodiraj(geslo)])
    c.close()
    id_uporabnika = c.lastrowid  
    return id_uporabnika

def preveri_geslo(up_ime, geslo):
    '''Preveri èe je v bazi uporabnik z podanim uporabniškim imenom in podanim geslom'''
    with baza:
        baza.execute('''SELECT id FROM uporabniki WHERE up_ime = ? AND geslo = ?''', [up_ime, zakodiraj(geslo)])
        id_uporabnika = baza.fetchone()
        if id_uporabnika is None: 
            raise Exception('vnešeno uporabniško ime ali geslo je napacno')




@route('/')
@get('/') # or @route('/login')
#Naslednji dve funkciji konstruirata login stran
def login():
    return '''
        <h1 align="center"> Dobrodošli!</h1>
        <center>
        <form action="/login" method="post">
            Uporabniško ime: <input name="username" type="text" />
            Geslo: <input name="password" type="password" />
            <input value="Vpis" type="submit" />
        </form>
        <p>Pred vami se nahaja spletna aplikacija za nadzor finančnega
        stanja podjetja. Za vpis potrebujete svoje uporabniško ime
        in geslo.
        </p>
        </center>
    '''
def check_login(username,password):
    if username == 'Jan' and password == 'Potocnik':
        #tukaj bo potrebno pogledati, če se ujema s kakim parom iz baze uporabnikov.
        return True
    else:
        return False
@post('/login') # or @route('/login', method='POST')
def do_login():
    username = request.forms.get('username')
    password = request.forms.get('password')
    if check_login(username, password):
        return urejanje()
    else:
        return "<p>Neuspešna prijava.</p>"

@route('/urejanje')
def urejanje(): 
    return '''
        <h1 align="center"> Informacije o poslovanju </h1>        
    '''

    

run(host = "localhost", port=8080, debug = True)
