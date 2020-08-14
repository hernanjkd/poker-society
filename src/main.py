import os; import re; import io; import csv; import json
import actions; import requests
import utils; import seeds
import pandas as pd
from flask import ( Flask, request, jsonify, render_template, send_file, 
    make_response, redirect )
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

jwt = JWTManager(app)
SetupAdmin(app)



######################################################################
# Takes in a dictionary with id, role and expiration date in minutes
#        create_jwt({ 'id': 100, 'role': 'admin', 'exp': 15 })
######################################################################
@jwt.jwt_data_loader
def add_claims_to_access_token(data):
    data = data if isinstance(data, dict) else {}
    now = datetime.utcnow()
    return {
        'exp': now + timedelta( days=data.get('exp', 400) ),
        'sub': data.get('id'),
        'role': data.get('role'),
        'iat': now,
        'nbf': now,
    }



@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code




@app.route('/reset_database')
def reset_database():
    seeds.run()
    return 'seeds ran'



@app.route('/testing/<filename>')
def testing(filename):
    resp = make_response( redirect('/upload/files') )
    resp.set_cookie( 'pokersociety_jwt', 'hi jwt' )
    return resp



@app.route('/users', methods=['POST'])
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



@app.route('/', methods=['GET','POST'])
@app.route('/users/login', methods=['GET','POST'])
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
        return jsonify({
            'login': False,
            'message':'Email and password are incorrect',
        })
    
    return jsonify({
        'login': True,
        'jwt': create_jwt({'id':user.id, 'role':'admin'})
    })
    


@app.route('/upload/files', methods=['GET','POST'])
def file_upload():

    # If user not logged in, send him to login page
    try:
        jwt = request.cookies.get('pokersociety-jwt')
        decode_jwt( jwt )
    except: 
        return redirect('/users/login')


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

 
    # TOURNAMENTS
    if utils.are_headers_for('tournaments', headers):

        returned_data = actions.process_tournament_excel( df )

        updated_df, error_list, trmnt_added = returned_data

        # updated_df = df # DELETE, ONLY FOR TESTING
        # error_list = [] # DELETE, ONLY FOR TESTING

        # Save file with added Tournament IDs, which will be downloaded in the frontend
        if trmnt_added:
            writer = pd.ExcelWriter(
                f"{os.environ['APP_PATH']}/src/excel_downloads/{f.filename}" )
            df.to_excel( writer, index=False )
            writer.save()

        # Display any errors that happened while processing the file
        if len(error_list) > 0:
            return jsonify({
                'download': trmnt_added,
                'error': error_list
            })

        msg = 'Tournament excel processed successfully'
        return jsonify({
            'message': msg+'. File downloaded' if trmnt_added else msg,
            'download': trmnt_added
        }), 200
            
    

    # CASINOS
    if utils.are_headers_for('casinos', headers):
        
        actions.process_casinos_excel( df )
        
        return jsonify({'message':
            'Casino excel proccessed successfully'}), 200


    # RESULTS
    if utils.are_headers_for('results', headers):
        
        swapprofit_json, log = actions.process_results_excel( df )

        swapprofit = Subscribers.query.filter_by(company_name='Swap Profit').first()
        if swapprofit is None:
            return jsonify({'error': 'Swap Profit not a subscriber'})

        if swapprofit_json is not None:
            resp = requests.post( swapprofit.api_host + '/results/update',
                json={
                    'api_token': utils.sha256( os.environ['API_TOKEN'] ),
                    **swapprofit_json
                })
            if not resp.ok:
                log = {'error': 'There was a problem in Swap Profit'}
            else:
                log = resp.json()


        return jsonify(log), 200




    return jsonify({'error': 'Unrecognized file'}), 200



@app.route('/download/file/<filename>')
def download_file(filename):
    path = f"{os.environ['APP_PATH']}/src/excel_downloads/{filename}"   
    return send_file( path, cache_timeout=0, as_attachment=True,
        attachment_filename=filename )



@app.route('/users/<id>', methods=['GET','PUT'])
def get_update_user(id):

    if id.isnumeric():
        user = Users.query.get( int(id) )
    else: # email
        user = Users.query.filter_by( email=id ).first()
    
    if user is None:
        raise APIException('User not found with id: '+ id, 404)

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
    
    trmnt = Tournaments.query.get( id )

    results = Results.query.filter_by( tournament_id=id ) \
                            .order_by( Results.place.asc() )
    
    template_data = {}
    if trmnt:
        template_data['trmnt_name'] = trmnt.name
        if trmnt.casino:
            template_data['casino'] = trmnt.casino.name

    if results.count() == 0:
        results = False
    
    else:
        obj = []
        for x in results:
            obj.append({
                'place': x.place,
                'full_name': x.full_name,
                'winnings': x.winnings,
                'nationality': x.nationality
            })
        results = json.dumps(obj)

    
    return render_template('results_table.html',
        **template_data,
        results = json.dumps(obj)
    )



# Endpoint to create and return the user id to swap profit
@app.route('/swapprofit/user', methods=['POST'])
def swapprofit_user():

    json = request.get_json()
    utils.check_params(json, 'api_token', 'email', 'password', 'first_name',
        'last_name')

    if json['api_token'] != utils.sha256( os.environ['API_TOKEN'] ):
        raise APIException('Invalid api token', 400)

    # Find user in db
    user = Users.query.filter_by( email=json['email'] ).first()
    
    # If no user found, create one
    if user is None:
        user = Users(
            email = json['email'],
            password = json['password'],
            first_name = json['first_name'],
            last_name = json['last_name'],
            nickname = json.get('nickname'),
            hendon_url = json.get('hendon_url'),
            status = 'valid'
        )
        db.session.add( user )
        db.session.commit()

    return jsonify({'pokersociety_id': user.id})



# Update email when user updates his email in swap profit
@app.route('/swapprofit/email/user/<int:id>', methods=['PUT'])
def swapprofit_email_update(id):

    json = request.get_json()
    utils.check_params(json, 'api_token', 'email')

    if json['api_token'] != utils.sha256( os.environ['API_TOKEN'] ):
        raise APIException('Invalid api token', 400)

    user = Users.query.get(id)
    user.email = json['email']
    db.session.commit()

    return jsonify({'message':'ok'}), 200



@app.route('/swapprofit/update')
def swapprofit_update():

    # Defaults to hours=1
    span = request.args.get('span', 'hours')
    amount = request.args.get('amount', 1)

    if span not in ['hours','days','all']:
        raise APIException('Invalid span: '+ span, 400)
    
    if span == 'all':
        trmnts = Tournaments.query.all()
    else:
        time_ago = datetime.utcnow() - timedelta( minutes=5, **{span:amount} )
        trmnts = Tournaments.query.filter( Tournaments.updated_at > time_ago )
    
    return jsonify([ x.swapprofit_serialize() for x in trmnts ])



# Endpoint to get the player ids that have swaps in the trmnt
@app.route('/users/tournament/<int:id>')
def get_all_users_in_trmnt(id):

    swapprofit = Subscribers.query.filter_by(company_name='Swap Profit').first()
    if swapprofit is None:
        return 'Swap Profit not a subscriber'

    resp = requests.post( 
        swapprofit.api_host + '/users/tournament/' + str(id),
        json={'api_token': utils.sha256( os.environ['API_TOKEN'] )} )

    if not resp.ok:
        return 'There was an error in Swap Profit'

    return jsonify(resp.json())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3333, debug=False)
