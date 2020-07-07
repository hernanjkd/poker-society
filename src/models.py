from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

db = SQLAlchemy()


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
    last_name = db.Column(db.String(100), nullable=False)
    nickname = db.Column(db.String(100))
    nationality = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # results = db.relationship('Results', back_populates='user')

    def __repr__(self):
        return f'<Users {self.email}>'

    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'status': self.status._value_,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'nickname': self.nickname,
            'nationality': self.nationality,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }


class Casinos(db.Model):
    __tablename__ = 'casinos'
    id = db.Column(db.String(10), primary_key=True, nullable=False)
    name = db.Column(db.String(500), nullable=False)
    address = db.Column(db.String(200))
    city = db.Column(db.String(50))
    state = db.Column(db.String(20))
    zip_code = db.Column(db.String(14))
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    time_zone = db.Column(db.String(50))
    website = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    facebook = db.Column(db.String(50))
    twitter = db.Column(db.String(50))
    instagram = db.Column(db.String(50))
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
            'time_zone': self.time_zone,
            'website': self.website,
            'phone': self.phone,
            'facebook': self.facebook,
            'twitter': self.twitter,
            'instagram': self.instagram,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


class Tournaments(db.Model):
    __tablename__ = 'tournaments'
    id = db.Column(db.Integer, primary_key=True)
    casino_id = db.Column(db.String(10), db.ForeignKey('casinos.id'))
    multiday_id = db.Column(db.String(25), default=None)
    name = db.Column(db.String(500), nullable=False)
    h1 = db.Column(db.String(200))
    buy_in = db.Column(db.String(20))
    blinds = db.Column(db.String(20))
    starting_stack = db.Column(db.String(20))
    results_link = db.Column(db.String(500))
    structure_link = db.Column(db.String(500))
    start_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    casino = db.relationship('Casinos', back_populates='tournaments')
    flights = db.relationship('Flights', back_populates='tournament')
    # results = db.relationship('Results', back_populates='tournament')

    def __repr__(self):
        return f'<Tournament {self.name}>'

    def swapprofit_serialize(self):
        from_trmnt = ['id','name','results_link','start_at']
        from_casino = ['address','city','state','zip_code','time_zone','latitude','longitude']
        return {
            'updated_at': self.updated_at,
            'tournament': { 'casino': self.casino.name,
                **{attr: getattr(self, attr) for attr in from_trmnt},
                **{attr: getattr(self.casino, attr) for attr in from_casino} },
            'flights': [
                {'id':f.id,'day':f.day,'start_at':f.start_at,'tournament_id':f.tournament_id} 
                for f in self.flights ]
        }

    def serialize(self):
        return {
            'id': self.id,
            'casino_id': self.casino_id,
            'name': self.name,
            'h1': self.h1,
            'buy_in': self.buy_in,
            'blinds': self.blinds,
            'starting_stack': self.starting_stack,
            'results_link': self.results_link,
            'structure_link': self.structure_link,
            'start_at': self.start_at,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'flights': [x.serialize() for x in self.flights]
        }


class Flights(db.Model):
    __tablename__ = 'flights'
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'))
    start_at = db.Column(db.DateTime)
    day = db.Column(db.String(5), default=None)
    notes = db.Column(db.String(3000))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tournament = db.relationship('Tournaments', back_populates='flights')

    def __repr__(self):
        return f'<Flights tournament:{self.tournament.name} {self.start_at} - {self.end_at}>'

    def serialize(self):
        return {
            'id': self.id,
            'tournament_id': self.tournament_id,
            'start_at': self.start_at,
            'day': self.day,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


class Results(db.Model):
    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer)#, db.ForeignKey('tournaments.id'))
    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    full_name = db.Column(db.String(40))
    nationality = db.Column(db.String(30))
    place = db.Column(db.String(6))
    winnings = db.Column(db.String(30), default=None)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # tournament = db.relationship('Tournaments', back_populates='results')
    # user = db.relationship('Users', back_populates='results')

    def __repr__(self):
        return f'<Results user:{self.user.last_name} tournament:{self.tournament.name}>'

    def serialize(self):
        return {
            'id': self.id,
            'tournament_id': self.tournament_id,
            # 'user_id': self.user_id,
            'full_name': self.full_name,
            'nationality': self.nationality,
            # 'email': user and self.user.email,
            'place': self.place,
            'winnings': self.winnings,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


class Subscribers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100))
    api_host = db.Column(db.String(100))
    api_token = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Subscribers {self.company_name}>'

    def serialize(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'api_host': self.api_host,
            'api_token': self.api_token,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }