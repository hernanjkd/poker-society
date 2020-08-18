import os
import utils
import pandas as pd
from sqlalchemy import or_
from utils import APIException
from models import db, Users, Casinos, Tournaments, Flights, Results
from datetime import datetime


def process_tournament_excel(df):

    error_list = []
    trmnt_added = False

    for index, r in df.iterrows():
        
        if str(r['Tournament']).strip() in ['','NaT']:
            continue

        trmnt_name, flight_day = utils.resolve_name_day( r['Tournament'] )
        start_at = datetime.strptime( 
            str(r['Date'])[:10] + str(r['Time']),
            '%Y-%m-%d%H:%M:%S' )

        casino_id = r['Casino ID']
        casino = Casinos.query.get( casino_id )
        if casino is None:
            msg = f'Casino with id {casino_id} not found'
            if msg not in error_list:
                error_list.append(msg)
            continue


        # Used for new tournaments and for updating existing ones
        trmntjson = {
            'name': trmnt_name,
            'start_at': start_at,
            'casino_id': casino_id,
            'multiday_id': r['Multi ID'].strip(),
            'h1': r['H1'].strip(),
            'buy_in': str( r['Buy-in'] ).strip(),
            'blinds': str( r['Blinds'] ).strip(),
            'results_link': str( r['Results Link'] ).strip(),
            'starting_stack': str( r['Starting Stack'] ).strip(),
            'structure_link': r['Structure Link'].strip()
        }
        flightjson = {
            'day': flight_day,
            'start_at': start_at, 
            'notes': r['NOTES - LOU'].strip()
        }


        # If the tournament id hasn't been saved, it could be a new tournament
        if str(r['Tournament ID']).strip() == '':

            if flight_day is not None:              
                # Check to see if trmnt has been saved already
                trmnt = Tournaments.query.filter_by(
                    multiday_id = r['Multi ID'].strip() ).first()
            
            if flight_day is None or trmnt is None:
                trmnt = Tournaments( **trmntjson )
                db.session.add( trmnt )
                db.session.flush()
            
            db.session.add( Flights(
                tournament_id = trmnt.id,
                **flightjson
            ))
            
            # save trmnt.id in the file
            df.at[index,'Tournament ID'] = trmnt.id
            trmnt_added = True

        
        else:
            trmnt = Tournaments.query.get( r['Tournament ID'] )
            if trmnt is None:
                error_list.append(f'Can\'t find tournament with id: "{r["Tournament ID"]}"')
                continue
            
            flight = Flights.query.filter_by( tournament_id=trmnt.id ) \
                .filter( or_( Flights.day == flight_day, Flights.start_at == start_at )) \
                .first()
            if flight is None:
                error_list.append(
                    f'Can\'t find Flight tournament_id: {trmnt.id}, '
                    f'day: {flight_day}, start_at: {start_at}' )
                continue

            for db_column, value in flightjson.items():
                if getattr(flight, db_column) != value:
                    setattr( flight, db_column, value )

            first_day = ['1', '1A']
            if flight_day in first_day:
                for db_column, value in trmntjson.items():
                    if getattr(trmnt, db_column) != value:
                        setattr( trmnt, db_column, value )


    db.session.commit()

    return df, error_list, trmnt_added


def process_casinos_excel(df):
    
    for index, r in df.iterrows():
        
        if '' in [ r['CASINO'].strip(), r['LONG'], r['LAT'] ]:
            continue

        casino = Casinos.query.get( r['ID'] )    

        casinojson = {
            'id': r['ID'].strip(),
            'name': r['CASINO'].strip(),
            'address': r['ADDRESS'].strip(),
            'city': r['CITY'].strip(),
            'state': r['STATE (FULL)'].strip(),
            'zip_code': str( r['ZIP CODE'] ).strip(),
            'website': r['WEBSITE'].strip(),
            'latitude': float(r['LAT']),
            'longitude': float(r['LONG']),
            'time_zone': r['TIME ZONE'].strip(),
            'phone': str( r['PHONE NUMBER'] ).strip(),
            'facebook': r['FACEBOOK'].strip(),
            'twitter': r['TWITTER'].strip(),
            'instagram': r['INSTAGRAM'].strip()
        }
    
        if casino is None:
            db.session.add( Casinos( **casinojson ))
        else:
            # Check for updates
            for attr, val in casinojson.items():
                if getattr(casino, attr) != val:
                    setattr(casino, attr, val)
            
        db.session.commit()
        
    return


def process_results_excel(df):
    '''
    {
        "tournament_id": 45,
        "tournament_buyin": 150,
        "users": {
            "sdfoij@yahoo.com": {
                "place": 11,
                "winnings": 200
            }
        }
    }
    '''
    trmnt_data = {}

    for index, r in df.iterrows():

        # Get the trmnt data that's in the first row
        if index == 0:
            
            # Check trmnt existance
            trmnt = Tournaments.query.get( r['Tournament ID'] )
            if trmnt is None:
                return None, {
                    'error':'This tournament ID was not found: '+ str(r['Tournament ID'])
                }

            trmnt.results_link = (os.environ['API_HOST'] + '/results/tournament/' +
                str(r['Tournament ID']) )

            # Check to see if file was uploaded already
            entry = Results.query.filter_by(
                tournament_id = r['Tournament ID']
            ).first()
            
            if entry is not None:
                return None, {
                    'error':'This tournament ID has already been uploaded: '+ str(trmnt.id)
                }
            
            # Swap Profit JSON
            trmnt_data = {
                'tournament_id': trmnt.id,
                'tournament_buyin': trmnt.buy_in,
                'users': {}
            }


        user_id = r['User ID'] or None
        
        # Add user to the Swap Profit JSON
        if user_id:
            user = Users.query.get( user_id )
            if user is None:
                db.session.rollback()
                return None, {
                    'error':'Couldn\'t find user with ID: '+ str(user_id)
                }
            
            # Swap Profit JSON
            trmnt_data['users'][user.email] = {
                'place': r['Place'],
                'winnings': r['Winnings']
            }

        # Add to database
        db.session.add( Results(
            tournament_id = trmnt_data['tournament_id'],
            user_id = user_id,
            full_name = r['Full Name'],
            place = r['Place'],
            nationality = r['Nationality'],
            winnings = r['Winnings']
        ))

    # If no errors, commit all data
    db.session.commit()
    
    return trmnt_data, {
        'message': 'Results excel processed successfully'
    }