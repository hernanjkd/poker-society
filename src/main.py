import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from admin import SetupAdmin
from utils import APIException, check_params, update_table, sha256, resolve_pagination
from models import db, Users, Casinos, Tournaments, Flights
from datetime import datetime, timedelta
from sqlalchemy import asc, desc

app = Flask(__name__)
app.url_map.strict_slashes = False
app.secret_key = os.environ.get('FLASK_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)

SetupAdmin(app)

@app.route('/testing')
def home():
    return jsonify([x.serialize() for x in Users.query.all()])


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


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
