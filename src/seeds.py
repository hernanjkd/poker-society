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

    db.session.commit()


    db.session.add( Users(
        email = 'lou@gmail.com',
        password = sha256('loustadler'),
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
        email='gherndon5@gmail.com',
        password=sha256('casper5'),
        first_name = 'Gabriel',
        nickname = '',
        last_name = 'Herndon',
        hendon_url= None,
        nationality = 'USA'
    ))
    db.session.add( Users(
        email='lou@pokersociety.com',
        password=sha256('swaptest'),
        first_name = 'Luiz',
        nickname = 'Lou',
        last_name = 'Stadler',
        hendon_url= 'https://pokerdb.thehendonmob.com/player.php?a=r&n=207424',
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
    db.session.add( Users(
        email='leff1117@aol.com',
        password=sha256('eatme'),
        first_name = 'Bobby',
        nickname = '',
        last_name = 'Leff',
        hendon_url='https://pokerdb.thehendonmob.com/player.php?a=r&n=187837',
        nationality = 'USA'
    ))
    

    # old_casino = Casinos(
    #     id='testing123',
    #     name='Old Vegas For Testing',
    #     city='Miami',
    #     state='FL',
    #     zip_code="33183",
    #     time_zone='EST',
    #     latitude='111',
    #     longitude='2222'
    # )
    # oldvegas = Tournaments(
    #     casino=old_casino,
    #     id=6,
    #     name='RRPO #21 - NLH $100,000 Guaranteed',
    #     buy_in='$200',
    #     start_at=datetime(1990,5,2,10)
    # )
    # flight1_oldvegas = Flights(
    #     start_at=datetime(1990,5,2,10),
    #     tournament=oldvegas,
    #     day='1A'
    # )
    # db.session.add_all([old_casino, oldvegas, flight1_oldvegas])

    # db.session.add( Results(
    #     user_id = None,
    #     full_name = 'Pedro Andres'
    # ))

    db.session.add( Subscribers(
        company_name = 'Swap Profit',
        api_host = 'https://swapprofit-beta.herokuapp.com', #'http://localhost:3000'
        api_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MTU4MTM1NTIsImlhdCI6MTU3OTgxMzU1MiwibmJmIjoxNTc5ODEzNTUyLCJzdWIiOjEsInJvbGUiOiJhZG1pbiJ9.1_rMYxvQtp2KiCGreT5frEMUApDh_hPx3322OZiiVa0"
    ))
    

    # Give room for Swap Profit to add mock tournaments
    db.session.execute("ALTER SEQUENCE tournaments_id_seq RESTART WITH 100")
    db.session.execute("ALTER SEQUENCE flights_id_seq RESTART WITH 100")


    db.session.commit()

    return