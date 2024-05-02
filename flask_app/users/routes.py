from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required, login_user, logout_user
from .. import bcrypt
import json 

# other imports
from ..forms import RegistrationForm, LoginForm, UpdateUsernameForm
from ..models import User, Itinerary

users = Blueprint("users", __name__)

@users.route('/register', methods=["GET", "POST"])
def register():
    # if user is already logged in, send to home page
    if current_user.is_authenticated:
        return redirect(url_for('trips.index'))
    
    form = RegistrationForm()
    
    # if form submission details are alright save in db
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, 
                    password=hashed)
        user.save()
        
        return redirect(url_for('users.login'))
    
    # otherwise re-render page
    return render_template('register.html', title="Register", form=form)

@users.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('trips.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()
        if (user is not None and bcrypt.check_password_hash(user.password, form.password.data)):
            login_user(user)
            return redirect(url_for('users.account'))
        else:
            flash(message="Authentication Error. Please Try Logging in Again")
    return render_template('login.html', title="Login", form=form)

@users.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('trips.index'))

@users.route('/account', methods=["GET", "POST"])
@login_required
def account():
    update_username_form = UpdateUsernameForm()
    if request.method == "POST":
        if update_username_form.submit_username.data and update_username_form.validate():
            new_username = update_username_form.username.data
            current_user.modify(username=new_username)
            return redirect(url_for("users.account"))

    itins = User.objects(username=current_user.username).first().itins
    links = []
    for itin in itins:
        print(json.dumps(itin.stations.split()))
        links.append(json.dumps(itin.stations.split()))

    return render_template(
        "account.html",
        current_user=current_user,
        update_username_form=update_username_form,
        zipped=zip(itins, links)
    )
