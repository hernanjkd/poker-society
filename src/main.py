import os
import csv
import requests
from flask import Flask, request, jsonify, render_template
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_simple import JWTManager, create_jwt, decode_jwt, get_jwt
from admin import SetupAdmin
from utils import APIException, check_params, update_table, sha256, resolve_pagination
from models import db, Users, Casinos, Tournaments, Flights, Results
from datetime import datetime, timedelta
from sqlalchemy import asc, desc
from io import StringIO

app = Flask(__name__)
app.url_map.strict_slashes = False
app.secret_key = os.environ.get('FLASK_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)

jwt = JWTManager(app)
SetupAdmin(app)



@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code



######################################################################
# Takes in a dictionary with id, role and expiration date in minutes
#        create_jwt({ 'id': 100, 'role': 'admin', 'exp': 15 })
######################################################################
@jwt.jwt_data_loader
def add_claims_to_access_token(kwargs={}):
    now = datetime.utcnow()
    kwargs = kwargs if isinstance(kwargs, dict) else {}
    id = kwargs.get('id')
    role = kwargs.get('role', 'invalid')
    exp = kwargs.get('exp', 15)

    return {
        'exp': now + timedelta(minutes=exp),
        'iat': now,
        'nbf': now,
        'sub': id,
        'role': role
    }



@app.route('/testing')
def testing():
    return 'ok'


x = 0
@app.route('/upload_files', methods=['GET','POST'])
def file_upload():

    # GET    
    if request.method == 'GET':
        return render_template('file_upload.html', 
                    host = os.environ.get('API_HOST'))

    # POST
    f = request.files['csv']

    # import time;time.sleep(1)
    # global x
    # x += 1
    # if x == 4:
    #     raise Exception('asdf')
    # return 'File processed successfully'
    
    f = StringIO( f.read().decode() )
    csv_reader = csv.reader( f, delimiter=',' )

    headers = {}
    lst = []
    header = True
    for row in csv_reader:
        json = {}
        for i, val in enumerate(row):
            if header:
                # date comes out like this: "﻿date"
                if i == 0 and 'Date' in val:
                    val = 'Date'
                json[str(i)] = val.lower().strip()
            else:
                h = headers[str(i)]
                json[h] = val.strip()
        if header:
            header = False
            headers = json
        else:
            lst.append(json)



    csv_headers = headers.values()

    # Tournaments
    tournament = True
    for header in ['tournament','buy-in','starting stack','blinds','structure link']:
        if header not in csv_headers:
            tournament = False
            break
    
    if tournament:
        
        for entry in lst:
            trmnt = Tournaments.query.filter_by( name=entry['tournament'] ).first()
            
            if trmnt is None:
                db.session.add( Tournaments(
                    casino_id = entry['casino_id'],
                    name = entry['tournament'],
                    buy_in = entry['buy-in'],
                    blinds = entry['blinds'],
                    starting_stack = entry['starting stack'],
                    results_link = entry['results link'],
                    structure_link = entry['structure link'],
                    # date goes here
                    notes = entry['notes']
                ))
        
            else:
                ref = {
                    'casino_id': 'casino_id',   'name': 'tournament',
                    'buy_in': 'buy-in',         'blinds': 'blinds',
                    'notes': 'notes',           # date goes here
                    'starting_stack': 'starting stack',
                    'results_link': 'results link',
                    'structure_link': 'structure link'
                }
                for obj_name, entry_name in ref.items():
                    if getattr(trmnt, obj_name) != entry[entry_name]:
                        setattr(trmnt, obj_name, entry[entry_name])


            db.session.commit()
            return 'Tournament csv has been proccessed successfully', 200

    
    # Venues
    else:
        venue = True
        for header in []:
            if header not in csv_headers:
                venue = False
                break
        
        if venue:
            for entry in lst:
                casino = Casino.query.filter_by( name=entry['name'] ).first()

                if casino is not None:
                    Casinos.query.delete()
                    db.session.execute("ALTER SEQUENCE casinos_id_seq RESTART")
                
                db.session.add( Casinos(
                    name = entry['name'],
                    address = entry['address'],
                    city = entry['city'],
                    state = entry['state'],
                    zip_code = entry['zip_code'],
                    longitude = entry['longitude'],
                    latitude = entry['latitude'],
                    website = entry['website']
                ))
                db.session.commit()
                return 'Venue csv has been proccessed successfully', 200

    # Results
    if results:
        data = {
            "tournament_id": 45,
            "tournament_buy_in": 150,
            "tournament_date": "23 Aug, 2020",
            "tournament_name": "Las Vegas Live Night Hotel",
            "results_link": "https://poker-society.herokuapp.com/results_link/234"
            "users": {
                "sdfoij@yahoo.com": {
                    "position": 11,
                    "winning_prize": 200
                }
            }
        }

        requests.post( os.environ.get('SWAP_PROFIT_API')+ '/results',
            data={ **data })

        return 'Results csv has been processed successfully', 200

    # return 'Unrecognized file'
    return jsonify({'headers': headers, 'entries': lst})



@app.route('/users', methods=['POST'])
def add_user():

    req = request.get_json()
    check_params(req, 'email', 'password', 'first_name', 'last_name')

    db.session.add( Users( **req ))
    db.session.commit()

    return jsonify({'message':'User added successfully'})



@app.route('/users/<int:id>', methods=['GET','PUT'])
def get_update_user(id):

    user = Users.query.get(id)
    if user is None:
        raise APIException('User not found', 404)
    
    if request.method == 'GET':
        return jsonify(user.serialize())

    req = request.get_json()
    check_params(req)

    update_table(user, req, ignore=['email','password'])
    db.session.commit()

    return jsonify(user.serialize())



@app.route('/casinos/<id>', methods=['GET'])
def get_casinos(id):

    if id == 'all':
        return jsonify([x.serialize() for x in Casinos.query.all()])

    if not id.isnumeric():
        raise APIException('Invalid id', 400)

    casino = Casinos.query.get(int(id))
    if casino is None:
        raise APIException('Casino not found', 404)

    return jsonify( casino.serialize() )



@app.route('/tournaments/<id>', methods=['GET'])
def get_tournaments(id):

    if id == 'all':
        now = datetime.utcnow() - timedelta(days=1)
        
        if request.args.get('history') == 'true':
            trmnts = Tournaments.query \
                        .filter( Tournaments.start_at < now ) \
                        .order_by( Tournaments.start_at.desc() )
        else:
            trmnts = Tournaments.query \
                        .filter( Tournaments.start_at > now ) \
                        .order_by( Tournaments.start_at.asc() )

        if trmnts.count() == 0:
            raise APIException('No tournaments for this query', 404)

        return jsonify([x.serialize() for x in trmnts])

    if not id.isnumeric():
        raise APIException('Invalid id', 400)

    trmnt = Tournaments.query.get(int(id))
    if trmnt is None:
        raise APIException('Tournament not found', 404)

    return jsonify(trmnt.serialize())



@app.route('/results/tournament/<int:id>')
def get_results(id):

    result = Results.query.filter_by( tournament_id = id) \
                        .order_by( Tournaments.position.asc() )
    
    if result is None:
        raise APIException('This tournament has no results yet', 404)
    
    return jsonify([x.serialize() for x in result])



@app.route('/zipcode/<id>')
def get_zipcodes(id):
    
    z = Zip_Codes.query.get( id )
    return jsonify(z.serialize()) if z else jsonify(None)




if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
