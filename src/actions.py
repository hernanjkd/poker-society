import os
import utils
import pandas as pd
from sqlalchemy import or_
from utils import APIException
from models import db, Users, Casinos, Tournaments, Flights, Results
from datetime import datetime


def process_tournament_excel(df):

    # file_header: db_column. Used to loop and check properties quicker
    trmnt_ref = {'Buy-in':'buy_in','Starting Stack':'starting_stack','Blinds':'blinds',
        'H1':'h1','Structure Link':'structure_link','Casino ID':'casino_id', 
        'Results Link':'results_link','Multi ID':'multiday_id'}
    
    error_list = []

    for index, r in df.iterrows():
        
        if r['Tournament'].strip() == '':
            continue

        trmnt_name, flight_day = utils.resolve_name_day( r['Tournament'] )
        start_at = datetime.strptime( 
            str(r['Date'])[:10] + str(r['Time']),
            '%Y-%m-%d%H:%M:%S' )
        

        # Used to loop and check properties quicker
        flight_ref = { 'start_at': start_at, 'day': flight_day,
            'notes': r['NOTES - LOU'].strip() }


        # If the tournament id hasn't been saved, it could be a new tournament
        if str(r['Tournament ID']).strip() == '':

            if flight_day is not None:              
                # Check to see if trmnt has been saved already
                trmnt = Tournaments.query.filter_by(
                    multiday_id = r['Multi ID'].strip() ).first()
            
            if flight_day is None or trmnt is None:
                trmnt = Tournaments(
                    name = trmnt_name,
                    start_at = start_at,
                    **{ db_column: str(r[file_header]).strip()
                        for file_header, db_column in trmnt_ref.items() }
                )
                db.session.add( trmnt )
                db.session.flush()
            
            db.session.add( Flights(
                tournament_id = trmnt.id,
                **flight_ref
            ))
            
            # save trmnt.id in the file
            df.at[index,'Tournament ID'] = trmnt.id

        
        else:
            trmnt = Tournaments.query.get( r['Tournament ID'] )
            if trmnt is None:
                error_list.append(f'Can\'t find Tournament id: "{r["Tournament ID"]}"')
                continue
            
            flight = Flights.query.filter_by( tournament_id=trmnt.id ) \
                .filter( or_( Flights.day == flight_day, Flights.start_at == start_at )) \
                .first()
            if flight is None:
                error_list.append(
                    f'Can\'t find Flight tournament_id: {trmnt.id}, '
                    f'day: {flight_day}, start_at: {start_at}' )
                continue

            for db_column, value in flight_ref.items():
                if getattr(flight, db_column) != value:
                    setattr( flight, db_column, value )

            first_day = ['1', '1A']
            if flight_day in first_day:
                for file_header, db_column in trmnt_ref.items():
                    entry = str(r[file_header]).strip()
                    if getattr(trmnt, db_column) != entry:
                        setattr( trmnt, db_column, entry )            
                if trmnt.start_at != start_at:
                    trmnt.start_at = start_at
                if trmnt.name != trmnt_name:
                    trmnt.name = trmnt_name


    db.session.commit()

    return [ df, error_list ]




def process_casinos_excel(df):

    ref = {'name':'CASINO','state':'STATE (FULL)','time_zone':'TIME ZONE',
        'city':'CITY','zip_code':'ZIP CODE','address':'ADDRESS',
        'website':'WEBSITE','phone':'PHONE NUMBER','facebook':'FACEBOOK',
        'twitter':'TWITTER','instagram':'INSTAGRAM','id':'ID'}
    
    for index, r in df.iterrows():
        
        if '' in [ r['CASINO'].strip(), r['LONG'], r['LAT'] ]:
            continue

        casino = Casinos.query.get( r['ID'] )    

        casino_json = {
            'latitude': float(r['LAT']),
            'longitude': float(r['LONG']),
            **{ db_column: r[file_header].strip()
                for db_column, file_header in ref.items() }
        }
    
        if casino is None:
            db.session.add( Casinos( **casino_json ))
        else:
            # Check for updates
            for attr, val in casino_json.items():
                if getattr(casino, attr) != val:
                    setattr(casino, attr, 
                        val.strip() if isinstance(val, str) else val)
            
        db.session.commit()
        
    return None