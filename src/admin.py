from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, AdminIndexView, expose, BaseView
from models import db, Users, Casinos, Tournaments, Flights, Results, \
    Subscribers


def SetupAdmin(app):

    class CustomView(ModelView):
        form_excluded_columns = ['created_at', 'updated_at']

    # class HomeView(AdminIndexView):
    #     @expose('/admin')
    #     def index(self):
    #         return self.render('file_upload.html')

    # class MyView(BaseView):
    #     @expose('/admin')
    #     def index(self):
    #         return self.render('file_upload.html')
    
    admin = Admin(app, name='Poker Society', template_mode='bootstrap3')

    # admin = Admin(app, name='Poker Society', template_mode='bootstrap3',
    #     index_view=AdminIndexView(
    #         name='File Upload',
    #         template='file_upload.html',
    #         url='/admin'
    #     )
    # )

    admin.add_views(
        CustomView( Users, db.session ),
        CustomView( Casinos, db.session ),
        CustomView( Tournaments, db.session ),
        CustomView( Flights, db.session ),
        CustomView( Results, db.session ),
        CustomView( Subscribers, db.session )
    )

    return admin