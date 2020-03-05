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
        'H1':'h1','Structure Link':'structure_link',#'Casino ID':'casino_id', 
        'Results Link':'results_link','Multi ID':'multiday_id'}
    
    error_list = []

    for index, r in df.iterrows():
        
        if r['Tournament'].strip() == '':
            continue

        trmnt_name, flight_day = utils.resolve_name_day( r['Tournament'] )
        start_at = datetime.combine( r['Date'].to_pydatetime(), r['Time'] )

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
                db.session.commit()
            
            db.session.add( Flights(
                tournament_id = trmnt.id,
                **flight_ref
            ))
            db.session.commit()
            
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




def process_venues_csv(csv_entries):

    id_list = []

    for entry in csv_entries:
        casino = Casinos.query.get( entry['casino id'] )    
        
        if casino is None:
            db.session.add( Casinos(
                name = entry['name'],
                address = entry['address'],
                city = entry['city'],
                state = entry['state'],
                zip_code = entry['zip code'],
                longitude = entry['longitude'],
                latitude = entry['latitude'],
                website = entry['website']
            ))

        else:
            for attr, val in entry:
                if getattr(casino, attr) != val:
                    setattr(casino, attr, val)

        db.session.commit()
        id_list.append({
            'id': casino.id,
            'name': entry['name'],
            'city': entry['city'],
            'state': entry['state']
        })

    return id_list