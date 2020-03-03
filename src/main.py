import os
import re
import io
import csv
import utils
import seeds
import actions
import requests
import pandas as pd
from flask import Flask, request, jsonify, render_template
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_simple import JWTManager, create_jwt, decode_jwt, get_jwt, jwt_required
from admin import SetupAdmin
from utils import APIException, role_jwt_required
from models import db, Users, Casinos, Tournaments, Flights, Results, Subscribers
from datetime import datetime, timedelta
from sqlalchemy import asc, desc

app = Flask(__name__)
app.url_map.strict_slashes = False
app.secret_key = os.environ.get('FLASK_KEY')
app.config['JWT_SECRET_KEY'] = 'super secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)

JWTManager(app)
SetupAdmin(app)



@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/jwt')
@jwt_required
def jwt():
    return jsonify(create_jwt(identity='hello'))

######################################################################
# Takes in a dictionary with id, role and expiration date in minutes
#        create_jwt({ 'id': 100, 'role': 'admin', 'exp': 15 })
######################################################################
# @jwt.jwt_data_loader
# def add_claims_to_access_token(kwargs={}):
#     now = datetime.utcnow()
#     kwargs = kwargs if isinstance(kwargs, dict) else {}
#     id = kwargs.get('id')
#     role = kwargs.get('role', 'invalid')
#     exp = kwargs.get('exp', 15)

#     return {
#         'exp': now + timedelta(minutes=exp),
#         'iat': now,
#         'nbf': now,
#         'sub': id,
#         'role': role
#     }



@app.route('/reset_database')
def reset_database():
    seeds.run()
    return 'seeds ran'



@app.route('/testing', methods=['POST'])
def testing(): 
    return 'testing'


@app.route('/user', methods=['POST'])
def register():

    json = request.get_json()
    utils.check_params(json, 'email')

    if 'password' in json:
        user = Users.query.filter_by(
            email = json['email'],
            password = utils.sha256( json['passowrd'] )
        )
        if user is None:
            raise APIException('User not found', 404)

        return jsonify({
            'jwt': create_jwt({
                'id': user.id,
                'role': 'user',
                'exp': 600
            })
        }), 200



@app.route('/user/login', methods=['GET','POST'])
def login():

    if request.method == 'GET':
        return render_template('login.html',
            host=os.environ.get('API_HOST'))

    json = request.get_json()
    utils.check_params(json, 'email', 'password')

    user = Users.query.filter_by( 
        email = json['email'],
        password = utils.sha256( json['password'] )
    ).first()
    if user is None:
        return render_template('login.html',
            host=os.environ.get('API_HOST'),
            message='Email and password are incorrect.')
    return 'ok'
    # return render_template('dashboard.html')

    # return jsonify({
    #     'jwt': create_jwt({
    #         'id': user.id,
    #         'role': 'user',
    #         'exp': 600
    #     })
    # }), 200



@app.route('/dashboard')
@role_jwt_required(['user'])
def get_user(user_id):
    pass
    


@app.route('/upload_files', methods=['GET','POST'])
# @role_jwt_required(['admin'])
def file_upload():
    
    # GET
    if request.method == 'GET':
        return render_template('file_upload.html', 
                    host = os.environ.get('API_HOST'))
    
    # POST
    if 'excel' not in request.files:
        raise APIException('"excel" property missing in the files array', 404)

    f = request.files['excel']
    df = pd.read_excel( f, keep_default_na=False )
    
    headers = list(df)

    if utils.are_headers_for('tournament', headers):

        updated_df, error_list = actions.process_tournament_excel( df )

        # Update Swap Profit
        swapprofit = Subscribers.query.filter_by(company_name='Swap Profit').first()
        if swapprofit is not None:
            r = requests.post(
                swapprofit.api_host +'/tournaments',
                headers = {'Authorization': 'Bearer '+ swapprofit.api_token},
                json = df.to_json(orient='records')
            )
            if not r.ok:
                error_list.append( r.content.decode("utf-8") )

        else: error_list.append('Swap Profit not a subscriber')

        if len(error_list) > 0:
            return jsonify(error_list)

        return 'Done'

    
    # Tournaments
    if utils.are_headers_for('tournament', csv_headers):

        swapprofit_json = actions.process_tournament_csv( csv_entries )
        
        f.save( os.path.join(os.getcwd(),'src/csv_uploads/tournaments/',f.filename) )
        
        swapprofit = Subscribers.query.filter_by(company_name='Swap Profit').first()
        if swapprofit is None:
            raise APIException('Swap Profit not a subscriber', 404)
        r = requests.post(
            swapprofit.api_host +'/tournaments',
            headers={'Authorization': 'Bearer '+ swapprofit.api_token},
            json=swapprofit_json
        )

        return r.json()['message']
            
    

    # Results
    if utils.are_headers_for('results', csv_headers):
        
        swapprofit_json = actions.process_results_csv( csv_entries )

        f.save( os.path.join(os.getcwd(),'src/csv_uploads/results/',f.filename) )
        requests.post( os.environ.get('SWAP_PROFIT_API')+ '/results',
            data = jsonify(swapprofit_json) )

        return jsonify({'message':'Results csv has been processed successfully'}), 200


    # Venues
    if utils.are_headers_for('venues', csv_headers):
        
        id_list = actions.process_venues_csv( csv_entries )

        f.save( os.path.join(os.getcwd(),'src/csv_uploads/venues/',f.filename) )
        return jsonify({
            'message':'Venue csv has been proccessed successfully',
            'id_list': id_list
        }), 200



    return jsonify({'message':'Unrecognized file'}), 200



@app.route('/users/<int:id>', methods=['GET','PUT'])
def get_update_user(id):

    user = Users.query.get(id)
    if user is None:
        raise APIException('User not found', 404)
    
    if request.method == 'GET':
        return jsonify(user.serialize())

    req = request.get_json()
    utils.check_params(req)

    utils.update_table(user, req, ignore=['email','password'])
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



@app.route('/roi/winning_swaps/<email>')
def get_roi_data(email): 
    
    user = Users.query.filter_by( email=email )
    if user is None:
        raise APIException('User not found', 404)

    won_trmnts = Results.query.filter( user_id=user.id ) \
                    .filter( Results.earnings != None )
    
    return jsonify(won_trmnts.count()), 200



if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
