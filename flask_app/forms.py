from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms_components import TimeField, DateTimeField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError

from .models import User

# naming the trip duh
class StartForm(FlaskForm):
    title = StringField(
        "Trip Name", validators=[InputRequired(), Length(min=1, max=50)]
        )
    start_time = DateTimeField("Start Time", validators=[InputRequired()])
    submit = SubmitField("Let's Go!")

# for creating routes/adding points of interest
# the time form from WTForms components returns a time in datetime.time standard:
# time(<hour>,<minute>,<second>,<microsecond>,...)
# the individual components can be accessed with . operator
# maybe make a validator that prevents doubling up on a point of interest
class POIForm(FlaskForm):
    poi = StringField("Enter a Point of Interest", validators=[InputRequired(), Length(max=50)])
    arrive = TimeField("Arrival Time", validators=[InputRequired()])
    depart = TimeField("Departure Time", validators=[InputRequired()])
    submit = SubmitField("Add to Trip")

# do we need email?
class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    # email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user is not None:
            raise ValidationError("This username is taken. Pick another username")

    # def validate_email(self, email):
    #     user = User.objects(email=email.data).first()
    #     if user is not None:
    #         raise ValidationError("Email is taken")

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