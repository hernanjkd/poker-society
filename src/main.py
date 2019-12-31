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
    f = request.files
    import time;time.sleep(1)
    global x
    x += 1
    if x == 4:
        raise Exception('asdf')
    return 'File processed successfully'

    f = StringIO( f.read().decode() )
    csv_reader = csv.reader( f, delimiter=',' )

    lst = []
    header = True
    for row in csv_reader:
        json = {}
        for i, val in enumerate(row):
            if header:
                json['h'+str(i)] = val.lower()
            else:
                h = lst[0]['h'+str(i)]
                json[h] = val
        lst.append(json)
        if header:
            header = False

    return jsonify(lst)



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
