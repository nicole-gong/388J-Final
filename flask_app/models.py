from flask_login import UserMixin
from . import db, login_manager
import dateutil

@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first()

class User(db.Document, UserMixin):
    username = db.StringField(min_length=1, 
                              max_length=40, 
                              unique=True, 
                              required=True)
    password = db.StringField(required=True)
    profile_pic = db.ImageField()

    def get_id(self):
        return self.username
