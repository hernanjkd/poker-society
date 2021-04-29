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
    d0 = datetime.utcnow() - timedelta(hours=17, minutes=1)
    d1 = datetime.utcnow() + timedelta(minutes=5)
    d2 = datetime.utcnow() - timedelta(hours=16, minutes=59)
    d3 = datetime.utcnow() + timedelta(days=300)
    d4 = datetime.utcnow() + timedelta(days=301)


    

    # past = Tournaments(
    #     casino=oneCasino,
    #     name='Past Demo Event',
    #     start_at= d0,
    #     buy_in_amount=100, 
    #     results_link= os.environ['API_HOST'] + '/results/tournament/100'
    # )
    # db.session.add(past)

    # flight1_past = Flights(
    #     start_at=past.start_at,
    #     tournament=past,
    # )
    # db.session.add(flight1_past)

    # Apple Demo Tournament and Flights
    # demo1 = Tournaments(
    #     casino=oneCasino,
    #     name="Apple Demo Event '22",
    #     start_at= d3,
    #     buy_in_amount=100
    # )
    # db.session.add(demo1)
    # flight1_demo1 = Flights(
    #     start_at=demo1.start_at,
    #     tournament=demo1,
    #     day='1A'
    # )
    # db.session.add(flight1_demo1)
    # flight2_demo1 = Flights(
    #     start_at=demo1.start_at + timedelta(hours=6),
    #     tournament=demo1,
    #     day='1B'
    # )
    # db.session.add(flight2_demo1)


    # Android Demo Tournament and Flights
    # demo2 = Tournaments(
    #     casino=oneCasino,
    #     name="Android Demo Event '22",
    #     start_at= d4,
    #     buy_in_amount=100
    # )
    # db.session.add(demo2)
    # flight1_demo2 = Flights(
    #     start_at=demo2.start_at,
    #     tournament=demo2,
    #     day='1A'
    # )
    # db.session.add(flight1_demo2)
    # flight2_demo2 = Flights(
    #     start_at=demo2.start_at + timedelta(hours=6),
    #     tournament=demo2,
    #     day="1B"
    # )
    # db.session.add(flight2_demo2)


    # ABOUT TO START TOURNAMENT
    # aboutToStart = Tournaments(
    #     casino=oneCasino,
    #     name='Example Live Event',
    #     start_at= d1,
    #     buy_in_amount=100
    # )
    # db.session.add(aboutToStart)
    # flight1_start = Flights(
    #     start_at=aboutToStart.start_at,
    #     tournament=aboutToStart,   
    # )
    # db.session.add(flight1_start)
    
    # ABOUT TO END TOURNAMENT
    # aboutToEnd = Tournaments(
    #     casino=oneCasino,
    #     name='Example End Event',
    #     start_at= d2,
    #     buy_in_amount=150
    # )
    # db.session.add(aboutToEnd)
    # flight1_end = Flights(
    #     start_at=aboutToEnd.start_at,
    #     tournament=aboutToEnd,
    # )
    # db.session.add(flight1_end)

    # OPEN TOURNAMENT #1
    # open1 = Tournaments(
    #     casino=oneCasino,
    #     name='Example Always Open Event #1',
    #     start_at= d3,
    #     buy_in_amount=150
    # )
    # db.session.add(open1)
    # flight1_open1 = Flights(
    #     start_at=d3,
    #     tournament=open1
    # )
    # db.session.add(flight1_open1)

    # OPEN TOURNAMENT #2
    # open2 = Tournaments(
    #     casino=oneCasino,
    #     name='Example Always Open Event #2',
    #     start_at= d4,
    #     buy_in_amount=250
    # )
    # db.session.add(open2)
    # flight1_open2 = Flights(
    #     start_at=d4,
    #     tournament=open2
    # )
    # db.session.add(flight1_open2)


    # db.session.add( Results(
    #     tournament_id = 100,
    #     user_id = 2,
    #     full_name = "Ally Allsion",
    #     place = '2nd',
    #     nationality = 'American',
    #     winnings = 5000
    # ))

    # db.session.add( Results(
    #     tournament_id = 100,
    #     user_id = 3,
    #     full_name = "Bobby Benderson",
    #     place = '4th',
    #     nationality = 'American',
    #     winnings = 3000
    # ))

   
    # db.session.add( Results(
    #     tournament_id = 100,
    #     user_id = 4,
    #     full_name = "Apple Demo Account",
    #     place = '6th',
    #     nationality = 'American',
    #     winnings = 500
    # ))

    # db.session.add( Results(
    #     tournament_id = 100,
    #     user_id = 5,
    #     full_name = "Android Demo Account",
    #     place = '7th',
    #     nationality = 'American',
    #     winnings = 400
    # ))

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