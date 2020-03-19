import os; import re; import io; import csv
import actions; import requests
import utils; import seeds
import pandas as pd
from flask import Flask, request, jsonify, render_template, send_file
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



@app.route('/testing/<filename>')
def testing(filename):
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

    swapprofit = Subscribers.query.filter_by(company_name='Swap Profit').first()
    if swapprofit is None:
        raise APIException('Swap Profit not a subscriber', 500)


    f = request.files['excel']
    df = pd.read_excel( f, keep_default_na=False )
    
    headers = list(df)

 
    # TOURNAMENTS
    if utils.are_headers_for('tournaments', headers):

        # updated_df, error_list = actions.process_tournament_excel( df )
        
        updated_df = df # DELETE, ONLY FOR TESTING
        error_list = [] # DELETE, ONLY FOR TESTING

        # Save file with added Tournament IDs
        writer = pd.ExcelWriter(
            f"{os.environ['APP_PATH']}/src/excel_downloads/{f.filename}" )
        df.to_excel( writer, index=False )
        writer.save()

        if len(error_list) > 0:
            return jsonify(error_list)

        return jsonify({
            'message':'Done. Downloading file',
            'download': True
        }), 200
            
    

    # RESULTS
    if utils.are_headers_for('results', headers):
            
        swapprofit_json = actions.process_results_csv( df )

        requests.post( os.environ.get('SWAPPROFIT_HOST')+ '/results',
            data = jsonify(swapprofit_json) )

        return jsonify({'message':
            'Results excel has been processed successfully'}), 200



    # CASINOS
    if utils.are_headers_for('casinos', headers):
        
        actions.process_casinos_excel( df )
        
        return jsonify({'message':
            'Casino excel has been proccessed successfully'}), 200



    return jsonify({'message':'Unrecognized file'}), 200



@app.route('/downloads/file/<filename>')
def download_file(filename):
    path = f"{os.environ['APP_PATH']}/src/excel_downloads/{filename}"   
    return send_file( path, cache_timeout=0, as_attachment=True,
        attachment_filename=filename )



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

    casino = Casinos.query.get( id )
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



@app.route('/swapprofit/update')
def swapprofit_update():

    if request.args.get('all') == 'true':
        trmnts = Tournaments.query.all()
    else:
        _1hr_ago = datetime.utcnow() - timedelta(days=30, minutes=5)
        trmnts = Tournaments.query.filter( Tournaments.updated_at > _1hr_ago )

    return jsonify([ x.swapprofit_serialize() for x in trmnts ])



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3333, debug=False)
