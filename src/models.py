from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

db = SQLAlchemy()

# association_table = db.Table('association', Base.metadata,
#     db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
#     db.Column('flight_id', db.Integer, db.ForeignKey('flight.id')))


class UserStatus(enum.Enum):
    valid = 'valid'
    pending = 'pending'
    unclaimed = 'unclaimed'
    pending_claim = 'pending_claim'

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    status = db.Column(db.Enum(UserStatus), default=UserStatus.unclaimed)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    results = db.relationship('Results', back_populates='user')
    buy_ins = db.relationship('Buy_ins', back_populates='user')
    # flights = db.relationship('Flights', secondary='Buy_ins', back_populates='users')

    def __repr__(self):
        return f'<Users {self.email}>'

    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'status': self.status._value_,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }


class Casinos(db.Model):
    __tablename__ = 'casinos'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    address = db.Column(db.String(200))
    city = db.Column(db.String(50))
    state = db.Column(db.String(20))
    zip_code = db.Column(db.String(14))
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    website = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tournaments = db.relationship('Tournaments', back_populates='casino')

    def __repr__(self):
        return f'<Casino {self.name}>'

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'website': self.website,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'tournaments': [x.serialize() for x in self.tournaments]
        }


class Tournaments(db.Model):
    __tablename__ = 'tournaments'
    id = db.Column(db.Integer, primary_key=True)
    casino_id = db.Column(db.Integer, db.ForeignKey('casinos.id'))
    name = db.Column(db.String(500), nullable=False)
    buy_in = db.Column(db.String(20))
    blinds = db.Column(db.Integer)
    starting_stack = db.Column(db.Integer)
    results_link = db.Column(db.String(500))
    structure_link = db.Column(db.String(500))
    start_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    casino = db.relationship('Casinos', back_populates='tournaments')
    flights = db.relationship('Flights', back_populates='tournament')
    results = db.relationship('Results', back_populates='tournament')

    def __repr__(self):
        return f'<Tournament {self.name}>'

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'casino_id': self.casino_id,
            'buy_in': self.buy_in,
            'blinds': self.blinds,
            'starting_stack': self.starting_stack,
            'results_link': self.results_link,
            'start_at': self.start_at,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'flights': [x.serialize() for x in self.flights]
        }


class Flights(db.Model):
    __tablename__ = 'flights'
    id = db.Column(db.Integer, primary_key=True)
    start_at = db.Column(db.DateTime)
    end_at = db.Column(db.DateTime)
    day = db.Column(db.Integer)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tournament = db.relationship('Tournaments', back_populates='flights')
    buy_ins = db.relationship('Buy_ins', back_populates='flight')
    # users = db.relationship('Users', secondary='Buy_ins', back_populates='flights')

    def __repr__(self):
        return f'<Flights tournament:{self.tournament.name} {self.start_at} - {self.end_at}>'

    def serialize(self):
        return {
            'id': self.id,
            'tournament_id': self.tournament_id,
            'start_at': self.start_at,
            'end_at': self.end_at,
            'day': self.day,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


class Buy_ins(db.Model):
    __tablename__ = 'buy_ins'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    flight_id = db.Column(db.Integer, db.ForeignKey('flights.id'))

    user = db.relationship('Users', back_populates='buy_ins')
    flight = db.relationship('Flights', back_populates='buy_ins')


class Results(db.Model):
    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    position = db.Column(db.Integer)
    winning_prize = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tournament = db.relationship('Tournaments', back_populates='results')
    user = db.relationship('Users', back_populates='results')

    def __repr__(self):
        return f'<Results user:{self.user.last_name} tournament:{self.tournament.name}>'

    def serialize(self):
        return {
            'id': self.id,
            'tournament_id': self.tournament_id,
            'user_id': self.user_id,
            'position': self.position,
            'winning_prize': self.winning_prize,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class Zip_Codes(db.Model):
    __tablename__ = 'zip_codes'
    zip_code = db.Column(db.String(14), primary_key=True)
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Zip_Codes {self.zip_code}>'

    def serialize(self):
        return {
            'zip_code': self.zip_code,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
