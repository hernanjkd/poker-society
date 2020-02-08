from utils import APIException
from models import db, Users, Casinos, Tournaments, Results
from datetime import datetime


def process_tournament_csv(csv_entries):

    swapprofit_json = []

    for entry in csv_entries:
        if entry['tournament'] == '':
            break

        entry['start_at'] = str( datetime.strptime(
            f"{entry['date']} {entry['time']}",
            '%d-%b-%y %I:%M %p') )
            
        trmnt = Tournaments.query.filter_by(
                    name = entry['tournament'],
                    start_at = entry['start_at']
                ).first()

        casino = Casinos.query.get( entry['casino id'] )
        if casino is None:
            raise APIException('Casino not found with id: '+entry['casino id'], 404)
        casino_data = {}
        for prop in ['address','city','state','zip_code','longitude','latitude']:
            casino_data[prop] = getattr(casino, prop)
        
        trmnt_json = {
            **entry,
            **casino_data
        }
        
        if trmnt is None:  
            new_trmnt = Tournaments(
                casino_id = entry['casino id'],
                name = entry['tournament'],
                h1 = entry['h1'],
                buy_in = entry['buy-in'],
                blinds = entry['blinds'],
                starting_stack = entry['starting stack'],
                results_link = entry['results link'],
                structure_link = entry['structure link'],
                start_at = entry['start_at'],
                notes = entry['notes']
            )
            db.session.add( new_trmnt )
            db.session.flush()

            trmnt_json['id'] = new_trmnt.id
    
        else:
            trmnt_json['id'] = trmnt.id
            db_fields = {'casino_id': 'casino id',  'name': 'tournament',
                'buy_in': 'buy-in', 'blinds': 'blinds', 'h1': 'h1',
                'notes': 'notes', 'start_at': 'start_at',
                'starting_stack': 'starting stack',
                'results_link': 'results link',
                'structure_link': 'structure link'}
            for db_name, entry_name in db_fields.items():
                if getattr(trmnt, db_name) != entry[entry_name]:
                    setattr(trmnt, db_name, entry[entry_name])
                    
        db.session.commit()
        swapprofit_json.append( trmnt_json )

    return swapprofit_json


def process_results_csv(csv_entries):

    tournament_name = None # get tournament name somehow
    trmnt = Tournaments.query.filter_by( name = tournament_name ).first()
    
    swapprofit_json = {
        "tournament_id": trmnt.id,
        "tournament_buy_in": trmnt.buy_in,
        "tournament_date": trmnt.start_at,
        "tournament_name": trmnt.name,
        "results_link": '', # find out how to get the results link
        "users": {
            # "sdfoij@yahoo.com": {
            #     "position": 11,
            #     "winnings": 200,
            #     "total_winning_swaps": 234
        }
    }

    for entry in csv_entries:
        
        user = Users.query.filter_by(
                    first_name = entry['first_name'],
                    middle_name = entry['middle_name'],
                    last_name = entry['last_name']
                ).first()

        user_id = user and user.id        
        won_swaps = Results.query.filter( user_id=user_id ) \
                                .filter( Results.winnings != None )
        won_swaps = won_swaps.count() if won_swaps is not None else 0

        swapprofit_json['users'][user.email] = {
            'position': entry['position'],
            'winnings': entry['winnings'],
            'total_winning_swaps': won_swaps
        }

        db.session.add( Results(
            tournament_id = trmnt.id,
            user_id = user.id if user is not None else None,
            first_name = entry['first_name'],
            middle_name = entry['middle_name'],
            last_name = entry['last_name'],
            nationality = entry['nationality'],
            position = entry['position'],
            winnings = entry['winnings']
        ))
        db.session.commit()

    return swapprofit_json


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