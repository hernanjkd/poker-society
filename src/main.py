import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from admin import SetupAdmin
from utils import APIException, generate_sitemap
from models import db, Users, Casinos, Tournaments, Flights

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)

SetupAdmin(app)

@app.route('/')
def home():
    return 'hello world'

@app.route('/user', methods=['POST'])
def add_user():

    req = request.get_json()

    db.session.add( Users(
        email = req['email'],
        password = req['password'],
        first_name = req['first_name'],
        last_name = req['last_name'],
        status = req.get('status', 'x')
    ))

    return jsonify([x.serialize() for x in Users.query.all()])


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
