from flask import Blueprint, render_template, url_for, request, redirect
from flask_login import login_required, current_user
import datetime
import dateutil

import folium
from folium.plugins import MarkerCluster
import pandas as pd

# other imports
from ..forms import StartForm, POIForm
from ..models import Trip, User
from .. import TripClient

# you need to register to create routes, so add flasklogin stuff and force loginrequired
# ok so what routes do we need that are trips related?
# TODO
# 1. a landing page obviously, this should have the name form in the middle
# 2. once we input a name we should go to one of two places - a login, or trip creation route
#   i.   trip creation route - a route that asks for time, and points of interest
#   ii.  this page should update when we add points of interest, it should be some visual list or smth
#   iii. it should also render in a small box below the name of the POI the metro that should be taken to reach that
#        location (so the metro route from A to B)
#   iv. there should be a button on the bottom of the page that says finish and just redirects to the account page

trips = Blueprint("trips", __name__)

@trips.route('/')
def index():
    data = TripClient.display_all()
    m = plot(data["stations"], data["lines"])
    m.get_root().width = "800px"
    m.get_root().height = "600px"
    iframe = m.get_root()._repr_html_()
    return render_template('index.html', iframe=iframe, stations=data["stations"], lines=data["lines"])

def plot(results, lines):
    coords = [38.9, -77]
    m = folium.Map(location=coords, zoom_start=13)
    for station in results.values():
        folium.Marker(
            location=station.coords,
            popup=station.name,
            icon=folium.plugins.BeautifyIcon(
                icon_shape="circle-dot", background_color="black"
            ),
        ).add_to(m)
    for line in lines:
        betweens = []
        for stop in line.stops:
            betweens.append(results[stop].coords)
        folium.PolyLine(betweens, color=line.name, weight=5).add_to(m)

    return m

@trips.route('/plan/<trip_title>')
@login_required
def plan_trip(trip_title):
    form = POIForm()
    trip = list(Trip.objects(title=trip_title))[-1]
    pois = list(trip.pois)
    
    if form.validate_on_submit():
        arrive = form.arrive.data
        depart = form.depart.data
        
        new_pois = pois.append(
            {
                "poi": form.poi.data,
                "arrival": f'{arrive.hour}:{arrive.minute}',
                "departure": f'{depart.hour}:{depart.minute}'
            })
        trip.modify(pois=new_pois)
        trip.save()
        
        # TODO add route computation between prev location and new added location
        
        # refresh page
        return redirect(url_for('trips.plan_trip', trip_title))
        
    return render_template('trip_planning.html', form=form, pois=pois)
