from models import db, Users, Casinos, Tournaments, Flights, Results, Subscribers
from datetime import datetime, timedelta
from utils import sha256
import os


def run():
    
    Flights.query.delete()
    Results.query.delete()

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
    d3 = datetime.utcnow() + timedelta(days=365)
    d4 = datetime.utcnow() + timedelta(days=366)


    oneCasino= Casinos(
        id='USFL001',
        name='Seminole Hard Rock Hotel & Casino',
        address='1 Seminole Way',
        city='Davie',
        state='FL',
        zip_code='33314',
        latitude=26.0510,
        longitude=-80.2097,
        time_zone='America/New_York',
    )

    aboutToStart = Tournaments(
        casino=oneCasino,
        name='Example Live Event',
        start_at= d1,
        buy_in_amount=100
    )
    db.session.add(aboutToStart)
    aboutToEnd = Tournaments(
        casino=oneCasino,
        name='Example End Event',
        start_at= d2,
        buy_in_amount=150
    )
    db.session.add(aboutToEnd)
    open1 = Tournaments(
        casino=oneCasino,
        name='Example Always Open Event #1',
        start_at= d3,
        buy_in_amount=150
    )
    db.session.add(open1)
    open2 = Tournaments(
        casino=oneCasino,
        name='Example Always Open Event #2',
        start_at= d4,
        buy_in_amount=250
    )
    db.session.add(open2)

    flight1_start = Flights(
        start_at=aboutToStart.start_at,
        tournament=aboutToStart,
        
    )
    db.session.add(flight1_start)

    flight1_end = Flights(
        start_at=aboutToEnd.start_at,
        tournament=aboutToEnd,
    )
    db.session.add(flight1_end)

    flight1_open1 = Flights(
        start_at=d3,
        tournament=open1
    )
    db.session.add(flight1_open1)
    flight1_open2 = Flights(
        start_at=d4,
        tournament=open2
    )
    db.session.add(flight1_open2)

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
        api_token = os.environ['API_TOKEN']
    ))
    
    # Give room for Swap Profit to add mock tournaments
    db.session.execute("ALTER SEQUENCE tournaments_id_seq RESTART WITH 100")
    db.session.execute("ALTER SEQUENCE flights_id_seq RESTART WITH 100")

    db.session.commit()

    return