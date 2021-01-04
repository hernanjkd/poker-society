from models import db, Users, Casinos, Tournaments, Flights, Results, Subscribers
from datetime import datetime, timedelta
from utils import sha256
import os


def run():
    
    Results.query.delete()
    Flights.query.delete()
    Tournaments.query.delete()
    Casinos.query.delete()
    Users.query.delete()
    Subscribers.query.delete()


    db.session.execute("ALTER SEQUENCE results_id_seq RESTART")
    db.session.execute("ALTER SEQUENCE flights_id_seq RESTART")
    db.session.execute("ALTER SEQUENCE tournaments_id_seq RESTART")
    db.session.execute("ALTER SEQUENCE users_id_seq RESTART")
    db.session.execute("ALTER SEQUENCE subscribers_id_seq RESTART")

    db.session.commit()
    d1 = datetime.utcnow() + timedelta(minutes=5)
    d2 = datetime.utcnow() - timedelta(hours=16, minutes=59)


    oneCasino= Casinos(
        id=1,
        name='Seminole Hard Rock Hotel & Casino',
        address='1 Seminole Way',
        city='Davie',
        state='FL',
        zip_code='33314',
        latitude=26.0510,
        longitude=-80.2097,
        time_zone='Etc/GMT-4'
    )

    aboutToStart = Tournaments(
        casino=oneCasino,
        name='Example Live Event',
        start_at= d1,
        buy_in='$100'
    )
    db.session.add(aboutToStart)
    aboutToEnd = Tournaments(
        casino=oneCasino,
        name='Example End Event',
        start_at= d2,
        buy_in='$150'
    )
    db.session.add(aboutToEnd)

    flight1_start = Flights(
        start_at=aboutToStart.start_at,
        tournament=aboutToStart,
        day=1
    )
    db.session.add(flight1_start)

    flight1_end = Flights(
        start_at=aboutToEnd.start_at,
        tournament=aboutToEnd,
        day=1
    )
    db.session.add(flight1_end)
    
    db.session.add( Users(
        email = 'lou@gsmail.com',
        password = sha256('loustadsler'),
        first_name = 'John',
        nickname = '',
        last_name = 'Doe',
        hendon_url='https://pokerdb.thehendonmob.com/player.php?a=r&n=207424',
        nationality = 'USA'
    ))
    db.session.add( Users(
        email='gherndon5@hotmail.com',
        password=sha256('casper5'),
        first_name = 'Cary',
        nickname = '',
        last_name = 'Katz',
        hendon_url='https://pokerdb.thehendonmob.com/player.php?a=r&n=26721',
        nationality = 'USA'
    ))
    db.session.add( Users(
        email='techpriest.gabriel@gmail.com',
        password=sha256('casper5'),
        first_name = 'Gabriel',
        nickname = '',
        last_name = 'Herndon',
        hendon_url= None,
        nationality = 'USA'
    ))
    

    db.session.add( Subscribers(
        company_name = 'Swap Profit',
        api_host = os.environ['SWAPPROFIT_API_HOST'],
        api_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MTU4MTM1NTIsImlhdCI6MTU3OTgxMzU1MiwibmJmIjoxNTc5ODEzNTUyLCJzdWIiOjEsInJvbGUiOiJhZG1pbiJ9.1_rMYxvQtp2KiCGreT5frEMUApDh_hPx3322OZiiVa0"
    ))
    
    # Give room for Swap Profit to add mock tournaments
    db.session.execute("ALTER SEQUENCE tournaments_id_seq RESTART WITH 100")
    db.session.execute("ALTER SEQUENCE flights_id_seq RESTART WITH 100")

    db.session.commit()

    return