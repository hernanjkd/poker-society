from models import db, Users, Casinos, Tournaments, Flights, Results, Subscribers
from pytz import timezone
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
    d3 = datetime.datetime.now(datetime.timezone.utc)
    d4 = datetime.utcnow()  


    oneCasino = Casinos(
        id='USFL001',
        name='Seminole Hard Rock Hotel & Casino',
        address='1 Seminole Way',
        city='Davie',
        state='FL',
        zip_code='33314',
        online=False,
        latitude=26.0510,
        longitude=-80.2097,
        time_zone='America/New_York',
    )
    db.session.add( oneCasino)

    db.session.add( Users(
        email='techpriest.gabriel@gmail.com',
        password=sha256('casper5'),
        first_name = 'Gabriel',
        nickname = '',
        last_name = 'Herndon',
        hendon_url= None,
        nationality = 'USA'
    ))
    
    db.session.add( Users(
        email='lou@thepokersociety.com',
        password=sha256('$wap1234!'),
        first_name = 'Lou',
        nickname = '',
        last_name = 'Stadler',
        hendon_url= None,
        nationality = 'USA'
    ))


        # ==========================================================
    #                   CURRENT TOURNAMENT - UNENTERED
    # ==========================================================
    
    # timezone = pytz.timezone("US/Eastern")

    design_unentered = Tournaments(
        casino=oneCasino,
        name='Test - Unentered Tournament',
        start_at= d3.astimezone(timezone('America/New_York')),
        buy_in_amount=100, 
        id=2222
    )
    db.session.add(design_unentered)
    flight1_design_unentered= Flights(
        start_at=design_unentered.start_at,
        tournament=design_unentered,
        id=2222
    )
    db.session.add(flight1_design_unentered)



    design_present = Tournaments(
        casino=oneCasino,
        name='Test - Present Tournament',
        start_at= d3.astimezone(timezone('America/New_York')),
        buy_in_amount=100, 
        id=5555
    )
    db.session.add(design_present)
    flight1_design_present = Flights(
        start_at=design_present.start_at,
        tournament=design_present,
        id=5555,
        day="1A"
    )
    db.session.add(flight1_design_present)
    flight2_design_present = Flights(
        start_at=design_present.start_at + timedelta(hours=6),
        tournament=design_present,
        id=5556,
        day="1B"
    )
    db.session.add(flight2_design_present)
    flight3_design_present = Flights(
        start_at=design_present.start_at + timedelta(hours=12),
        tournament=design_present,
        id=5557, 
        day="1C"
    )
    db.session.add(flight3_design_present)

    confirmed_past = Tournaments(
        id=7777,
        casino=oneCasino,
        name='Test - Results Submitted',
        start_at= d0,
        buy_in_amount=100, 
        results_link='http://poker-society.herokuapp.com/results/tournament/7777',
    )
    db.session.add(confirmed_past)
    flight1_confirmed_past = Flights(
        id=7777,
        start_at=confirmed_past.start_at,
        tournament=confirmed_past,
    )
    db.session.add(flight1_confirmed_past)
    results_alice = Results(
        full_name = "Allison Avery",
        tournament=confirmed_past,
        user_id=2,
        winnings=500,
        place="2nd",
        created_at = datetime.utcnow(),
        updated_at = datetime.utcnow(),
    )
    db.session.add(results_alice)

    results_bob = Results(
        full_name = "Bob Benderson",
        tournament=confirmed_past,
        user_id=3,
        winnings=1000,
        place="1st",
        created_at = datetime.utcnow(),
        updated_at = datetime.utcnow(),
    )
    db.session.add(results_bob)

    results_jose = Results(
        full_name = "Jose Hurtado",
        tournament=confirmed_past,
        user_id=6,
        winnings=100,
        place="3rd",
        created_at = datetime.utcnow(),
        updated_at = datetime.utcnow(),
    )
    db.session.add(results_jose)

    db.session.add( Subscribers(
        company_name = 'Swap Profit',
        api_host = os.environ['SWAPPROFIT_API_HOST'],
        api_token = os.environ['API_TOKEN']
    ))

    db.session.add( Subscribers(
        company_name = 'Poker Trader',
        api_host = os.environ['POKERTRADER_API_HOST'],
        api_token = os.environ['API_TOKEN']
    ))
    
    # Give room for Swap Profit to add mock tournaments
    db.session.execute("ALTER SEQUENCE tournaments_id_seq RESTART WITH 100")
    db.session.execute("ALTER SEQUENCE flights_id_seq RESTART WITH 100")

    db.session.commit()

    return