from models import db, Users, Casinos, Tournaments, Flights, Results, Subscribers
from datetime import datetime, timedelta
from utils import sha256


def run():

    Results.query.delete()
    Flights.query.delete()
    Tournaments.query.delete()
    Casinos.query.delete()
    Users.query.delete()
    Subscribers.query.delete()

    db.session.execute("ALTER SEQUENCE users_id_seq RESTART")
    db.session.execute("ALTER SEQUENCE tournaments_id_seq RESTART")
    db.session.execute("ALTER SEQUENCE flights_id_seq RESTART")
    db.session.execute("ALTER SEQUENCE results_id_seq RESTART")
    db.session.execute("ALTER SEQUENCE subscribers_id_seq RESTART")


    db.session.add( Users(
        email = 'lou@gmail.com',
        password = sha256('123'),
        first_name = 'Luiz',
        nickname = 'Lou',
        last_name = 'Stadler',
        hendon_url='https://pokerdb.thehendonmob.com/player.php?a=r&n=207424',
        nationality = 'USA'
    ))
    db.session.add( Users(
        email='hoang28974@gmail.com',
        password=sha256('kateHoang'),
        first_name = 'Kate',
        nickname = '',
        last_name = 'Hoang',
        hendon_url='https://pokerdb.thehendonmob.com/player.php?a=r&n=421758',
        nationality = 'USA'
    ))
    db.session.add( Users(
        email='katz234@gmail.com',
        password=sha256('carykatz'),
        first_name = 'Cary',
        nickname = '',
        last_name = 'Katz',
        hendon_url='https://pokerdb.thehendonmob.com/player.php?a=r&n=26721',
        nationality = 'USA'
    ))
    db.session.add( Users(
        email='mikitapoker@gmail.com',
        password=sha256('nikitapoker'),
        first_name = 'Nikita',
        nickname = 'Mikita',
        last_name = 'Bodyakovskiy',
        hendon_url='https://pokerdb.thehendonmob.com/player.php?a=r&n=159100',
        nationality = 'USA'
    ))
    db.session.add( Users(
        email='perry1830@msn.com',
        password=sha256('Kobe$$'),
        first_name = 'Perry',
        nickname = '',
        last_name = 'Shiao',
        hendon_url='https://pokerdb.thehendonmob.com/player.php?a=r&n=371190',
        nationality = 'USA'
    ))
    db.session.add( Users(
        email='leff1117@aol.com',
        password=sha256('eatme'),
        first_name = 'Bobby',
        nickname = '',
        last_name = 'Leff',
        hendon_url='https://pokerdb.thehendonmob.com/player.php?a=r&n=187837',
        nationality = 'USA'
    ))
    db.session.add( Users(
        email='neal_corcoran@yahoo.com',
        password=sha256('Brooklyn1'),
        first_name = 'Neal',
        nickname = '',
        last_name = 'Corcoran',
        hendon_url='https://pokerdb.thehendonmob.com/player.php?a=r&n=506855',
        nationality = 'USA'
    ))
    db.session.add( Users(
        email='brooklynbman@yahoo.com',
        password=sha256('Brooklyn1'),
        first_name = 'Brian',
        nickname = '',
        last_name = 'Gelrod',
        hendon_url='https://pokerdb.thehendonmob.com/player.php?a=r&n=239802',
        nationality = 'USA'
    ))


    oldvegas = Tournaments(
        id=884,
        name='RRPO #21 - NLH $100,000 Guaranteed',
        buy_in='$200',
        start_at=datetime(1990,5,2,10)
    )
    flight1_oldvegas = Flights(
        start_at=datetime(1990,5,2,10),
        tournament=oldvegas,
        day='1A'
    )
    db.session.add_all([oldvegas, flight1_oldvegas])

    coconut = Tournaments(
        id=882,	
        name='Live Tournament at Vegas Casino',
        buy_in='$500',
        start_at=datetime.utcnow() - timedelta(days=2),
    )
    db.session.add(coconut)

    db.session.add( Results(
        user_id = None,
        full_name = 'Pedro Andres'
    ))

    db.session.add( Subscribers(
        company_name = 'Swap Profit',
        api_host = 'https://swapprofit-beta.herokuapp.com', #'http://localhost:3000'
        api_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MTU4MTM1NTIsImlhdCI6MTU3OTgxMzU1MiwibmJmIjoxNTc5ODEzNTUyLCJzdWIiOjEsInJvbGUiOiJhZG1pbiJ9.1_rMYxvQtp2KiCGreT5frEMUApDh_hPx3322OZiiVa0"
    ))
    
    db.session.commit()