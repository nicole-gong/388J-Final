from flask import Blueprint, render_template, url_for, request, redirect
from flask_login import login_required, current_user
import datetime
import dateutil

import folium
from folium.plugins import MarkerCluster

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
stations = TripClient.display_stations()
lines = TripClient.display_lines()

@trips.route("/", methods=["GET", "POST"])
def index():
    m = plot(stations, lines)
    m.get_root().width = "1200px"
    m.get_root().height = "700px"
    iframe = m.get_root()._repr_html_()
    # if request.method == "POST":
    #     return redirect(url_for("trips.create_itin"))

    return render_template('index.html', iframe=iframe)

# @trips.route("/create_itin", methods=["GET", "POST"])
# def create_itin():
#     checked_stations = request.form.get("checked")
#     if not checked_stations: checked_stations = ["ERROR"]
#     m = plot(stations, lines)
#     m.get_root().width = "1200px"
#     m.get_root().height = "700px"
#     iframe = m.get_root()._repr_html_()
#     if request.method == 'POST':
#         return redirect(url_for("trips.create_itin"))

#     return render_template("create_itin.html", checked_stations=checked_stations, iframe=iframe)

def plot(stations, lines):
    coords = [38.9, -76.9]
    m = folium.Map(location=coords, zoom_start=12)
    for station in stations:
        html = folium.Html(
            f"<a href={url_for('trips.line_info',station_code=station)} target='_top'>{stations[station].name}</a>",
            # + f"<input type='checkbox' name='checked_box' id='{station}'>",
            script=True,
        )
        folium.Marker(
            location=stations[station].coords,
            popup=folium.Popup(html, show=True),
            icon=folium.plugins.BeautifyIcon(
                icon_shape="circle-dot", background_color="black"
            ),
        ).add_to(m)
    for line in lines:
        betweens = []
        for stop in lines[line].stops:
            betweens.append(stations[stop].coords)
        folium.PolyLine(betweens, color=lines[line].name, weight=5).add_to(m)

    return m

def plot_line(station, stations, lines):
    coords = [38.9, -76.9]
    m = folium.Map(location=coords, zoom_start=12)
    html = folium.Html(f"<a href={url_for('trips.line_info',station_code=station.code)}>{station.name}</a>", script=True)
    for line in lines:
        betweens = []
        for stop in lines[line].stops:
            betweens.append(stations[stop].coords)
            folium.Marker(
                location=stations[stop].coords,
                popup=folium.Popup(html),
                icon=folium.plugins.BeautifyIcon(icon_shape="circle-dot"),
            ).add_to(m)

        folium.Marker(
            location=station.coords,
            popup=folium.Popup(html),
            icon=folium.plugins.BeautifyIcon(
                icon_shape="doughnut", background_color="black"
            ),
        ).add_to(m)

        folium.PolyLine(betweens, color=lines[line].name, weight=5).add_to(m)

    return m

@trips.route("/line/<station_code>", methods=["GET"])
def line_info(station_code):
    data = TripClient.display_station(station_code)
    iframes = []
    dests = []
    for linecode in data.linecodes:
        if linecode:
            m = plot_line(data, stations, {linecode: lines[linecode]})
            m.get_root().width = "600px"
            m.get_root().height = "300px"
            iframe = m.get_root()._repr_html_()
            iframes.append(iframe)
            dests += TripClient.shortest_path(station_code, lines[linecode].start)
            dests += TripClient.shortest_path(station_code, lines[linecode].end)

    return render_template(
        "station.html", data=data, dests=dests, iframes=iframes)

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
