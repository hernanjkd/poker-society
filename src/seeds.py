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
        email = '123',
        password = sha256('123'),
        first_name = 'Luiz',
        nickname = 'Lou',
        last_name = 'Stadler',
        nationality = 'USA'
    ))
    db.session.add( Users(
        email='hoang28974@gmail.com',
        password=sha256('kateHoang'),
        first_name = 'Kate',
        nickname = '',
        last_name = 'Hoang',
        nationality = 'USA'
    ))
    db.session.add( Users(
        email='katz234@gmail.com',
        password=sha256('carykatz'),
        first_name = 'Cary',
        nickname = '',
        last_name = 'Katz',
        nationality = 'USA'
    ))
    db.session.add( Users(
        email='mikitapoker@gmail.com',
        password=sha256('nikitapoker'),
        first_name = 'Nikita',
        nickname = 'Mikita',
        last_name = 'Bodyakovskiy',
        nationality = 'USA'
    ))
    db.session.add( Users(
        email='perry1830@msn.com',
        password=sha256('Kobe$$'),
        first_name = 'Perry',
        nickname = '',
        last_name = 'Shiao',
        nationality = 'USA'
    ))
    db.session.add( Users(
        email='leff1117@aol.com',
        password=sha256('eatme'),
        first_name = 'Bobby',
        nickname = '',
        last_name = 'Leff',
        nationality = 'USA'
    ))
    db.session.add( Users(
        email='neal_corcoran@yahoo.com',
        password=sha256('Brooklyn1'),
        first_name = 'Neal',
        nickname = '',
        last_name = 'Corcoran',
        nationality = 'USA'
    ))
    db.session.add( Users(
        email='brooklynbman@yahoo.com',
        password=sha256('Brooklyn1'),
        first_name = 'Brian',
        nickname = '',
        last_name = 'Gelrod',
        nationality = 'USA'
    ))

    db.session.add( Results(
        user_id = None,
        full_name = 'Pedro Andres'
    ))

    db.session.add( Subscribers(
        company_name = 'Swap Profit',
        api_host = 'http://localhost:3000',
        api_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MTU4MTM1NTIsImlhdCI6MTU3OTgxMzU1MiwibmJmIjoxNTc5ODEzNTUyLCJzdWIiOjEsInJvbGUiOiJhZG1pbiJ9.1_rMYxvQtp2KiCGreT5frEMUApDh_hPx3322OZiiVa0"
    ))
    
    db.session.commit()