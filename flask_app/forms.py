from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    PasswordField,
)
from wtforms_components import TimeField, DateTimeField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError

from .models import User, Itinerary 

class ItinForm(FlaskForm):
    itin_name = StringField(
        "Itinerary Name:", validators=[InputRequired(), Length(min=1, max=40)]
    )
    submit = SubmitField("Generate Itinerary")
    
    def validate_itin_name(self, itin_name):
        name = Itinerary.objects(itin_name=itin_name.data).first()
        if name is not None:
            raise ValidationError("This itinerary name is taken. Please choose another.")

class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    password = PasswordField("Password", validators=[InputRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user is not None:
            raise ValidationError("This username is taken.")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=1, max=40)])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Submit")

class UpdateUsernameForm(FlaskForm):    
    username = StringField("New Username", validators=[InputRequired(), Length(min=1, max=40)])
    submit_username = SubmitField("Submit") 

    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user is not None:
            raise ValidationError("This username is taken. Pick another username")
