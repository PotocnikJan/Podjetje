from Bottle import *
import sqlite3
import hashlib
datoteka_baze = "Podjetje"
baza = sqlite3.connect(datoteka_baze,isolation_level=None)
########################################################
#                                                      #
# Prve tri funkcije so osnovne, in racunajo            #
# Promet podjetja, stroske, in nazadnje seveda         #
# zaslužek, ki ga je ustvarilo.                        #
########################################################
def izracunajPromet():
   
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
        baza.execute('''SELECT racuni.id_racuna,racuni.cena,racuni.datum
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
                        JOIN stranke ON stranke.id_stranke = racuni.id_stranke
                        WHERE datum > ?%''',[datum])


        return baza.fetchall()


########################################################
#                                                      #
# Tukaj se nahajajo funkcije, ki vstavljajo            #
# različne podatke v našo bazo.                        #
# Nove uporabnike, racune, prodane artikle ...         #
########################################################
    
def dodajNakup(seznamArtiklov):
    #seznamArtiklov vsebuje naravna števila, ki so ID-ji artiklov    
    '''V bazo dodamo nov račun in prodane artikle'''
    for i in seznamArtiklov:
        c = baza.cursor()
        c.execute('''INSERT INTO prodani_artikli (artikel,cena,ddv) VALUES (SELECT id, cena, ddv FROM artikli WHERE id = ?)''', [artikel])
        c.close()        
        id_artikla = c.lastrowid  
        return id_artikla
    for i in seznamArtiklov:
        pass
        
    
    
    
def dodajArtikel(artikel,cena,ddv):
    '''V bazo dodamo uporabnika: njegovo uporabniško ime in zakodirano geslo'''
    c = baza.cursor()
    c.execute('''INSERT INTO artikli (artikel,cena,ddv) VALUES (?,?,?)''', [artikel,cena,ddv])
    c.close()
    id_artikla = c.lastrowid  
    return id_artikla
def dodaj_strosek(vrsta_stroska, cena, ddv, datum):

    '''V bazo dodamo uporabnika: njegovo uporabniško ime in zakodirano geslo'''
    c = baza.cursor()
    c.execute('''INSERT INTO stroski (vrsta_stroska, cena, ddv, datum) VALUES (?, ?, ?, ?)''', [vrsta_stroska, cena, ddv, datum])
    c.close()
    id_stroska = c.lastrowid 
    return id_stroska
#######################################################################################################################
#Spodaj se nahajajo funkcije, ki poskrbijo, da lahko preverjamo verodostojnost uporabnikov, katerih dostopna          #
#Uporabniška imena in gesla se nahajajo v podatkovni bazi                                                             #
#######################################################################################################################
def zakodiraj(password):
    return hashlib.md5(password.encode()).hexdigest()

def dodaj_uporabnika(username, password):

    '''V bazo dodamo uporabnika: njegovo uporabniško ime in zakodirano geslo'''
    c = baza.cursor()
    c.execute('''INSERT INTO uporabniki (username, password) VALUES (?, ?)''', [username, zakodiraj(password)])
    c.close()
    id_uporabnika = c.lastrowid  
    return id_uporabnika





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
    '''Preveri èe je v bazi uporabnik z podanim uporabniškim imenom in podanim geslom'''
    with baza:
        cur = baza.execute('''SELECT id_uporabnika FROM uporabniki WHERE username = ? AND password = ?''', [username, zakodiraj(password)])
        id_uporabnika = cur.fetchone()
        return id_uporabnika is not None

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
