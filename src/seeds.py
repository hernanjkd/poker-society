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
        first_name = 'Lou',
        middle_name = '',
        last_name = 'Stadler',
        nationality = 'USA'
    ))

    db.session.add( Subscribers(
        company_name = 'Swap Profit',
        api_host = 'http://localhost:3000',
        api_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MTU4MTM1NTIsImlhdCI6MTU3OTgxMzU1MiwibmJmIjoxNTc5ODEzNTUyLCJzdWIiOjEsInJvbGUiOiJhZG1pbiJ9.1_rMYxvQtp2KiCGreT5frEMUApDh_hPx3322OZiiVa0"
    ))
    
    db.session.commit()