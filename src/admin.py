from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
from models import db, Users, Casinos, Tournaments, Flights


def SetupAdmin(app):

    class ExcludedModelView(ModelView):
        form_excluded_columns = ['created_at', 'updated_at']
    
    admin = Admin(app, name='Poker Society', template_mode='bootstrap3')

    admin.add_view( ExcludedModelView( Users, db.session ))
    admin.add_view( ExcludedModelView( Casinos, db.session ))
    admin.add_view( ExcludedModelView( Tournaments, db.session ))
    admin.add_view( ExcludedModelView( Flights, db.session ))

    return admin