import os
import csv
import requests
from flask import Flask, request, jsonify, render_template
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_simple import JWTManager, create_jwt, decode_jwt, get_jwt
from admin import SetupAdmin
from utils import APIException, check_params, update_table, sha256, resolve_pagination
from models import db, Users, Casinos, Tournaments, Flights, Results, Zip_Codes
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



def fetch_zipcodes():

    req = requests.get('https://assets.breatheco.de/apis/fake/zips.php')
    data = req.json()

    for zip in data:
        db.session.add( Zip_Codes(
            zip_code = zip['_id'],
            longitude = zip['loc'][0],
            latitude = zip['loc'][1]
        ))

    db.session.commit()

    return 'ok'

print('hello world')
print( requests.get('http://localhost:3333/zipcode/89145').json() )


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=False)
