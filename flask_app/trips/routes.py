from flask import Blueprint, render_template, url_for, request, redirect
from flask_login import login_required, current_user
import json

import folium
from folium.plugins import MarkerCluster

from ..models import User, Itinerary
from .. import TripClient
from ..forms import ItinForm

trips = Blueprint("trips", __name__)
stations = TripClient.display_stations()
lines = TripClient.display_lines()
coords = [38.9, -76.9]

@trips.route("/", methods=["GET", "POST"])
def index():
    m = plot()
    m.get_root().width = "1200px"
    m.get_root().height = "700px"
    iframe = m.get_root()._repr_html_()
    if request.method == "POST":
        return redirect(url_for("trips.create_itin", checked_stations= ''.join(request.form.get('checked'))))

    return render_template('index.html', iframe=iframe)

@trips.route("/create_itin/<checked_stations>", methods=["GET", "POST"])
def create_itin(checked_stations):
    checked_stations = checked_stations.replace("%2C" , ",")
    stations_list = checked_stations.split(",")
    display_stations = {}
    display_lines = {}
    for station_code in stations_list:
        station = stations[station_code]
        display_stations[station_code] = station
        for linecode in station.linecodes:
            if linecode and linecode not in display_lines:
                display_lines[linecode] = lines[linecode] 

    m = plot_few(display_stations, display_lines)
    m.get_root().width = "900px"
    m.get_root().height = "500px"
    iframe = m.get_root()._repr_html_()
    form = ItinForm()
    if form.validate_on_submit():
        itin = Itinerary(
            itin_name=form.itin_name.data,
            stations=checked_stations
        )
        user = User.objects(username=current_user.username).first()
        itin.save()
        user.update(push__itins=itin)
        return redirect(url_for("users.account"))

    return render_template("create_itin.html", itin_form=form, stations=stations, checked_stations=stations_list, iframe=iframe)

@trips.route("/line/<station_code>", methods=["GET"])
def line_info(station_code):
    data = TripClient.display_station(station_code)
    iframes = []
    dests = []
    for linecode in data.linecodes:
        if linecode:
            m = plot_one(data, {linecode: lines[linecode]})
            m.get_root().width = "800px"
            m.get_root().height = "300px"
            iframe = m.get_root()._repr_html_()
            iframes.append(iframe)
            dests += TripClient.shortest_path(station_code, lines[linecode].start)
            dests += TripClient.shortest_path(station_code, lines[linecode].end)
    itins = Itinerary.objects(stations__contains=station_code)
    links = []
    for itin in itins:
        links.append(json.dumps(itin.stations.split()))
    return render_template(
        "station.html", x=links, stations=stations, data=data, dests=dests, iframes=iframes, zipped=zip(itins, links))

def plot():
    m = folium.Map(location=coords, zoom_start=12)
    for station in stations:
        html = folium.Html(
            f"<div style='display: flex; flex-direction: column; justify-content: center; align-items: center;'> <a href={url_for('trips.line_info',station_code=station)} target='_top'>{stations[station].name}</a>"
            + f"<input type='checkbox' name='checked_box' id='{station}'> </div>",
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

def plot_few(this_stations, lines):
    m = folium.Map(location=coords, zoom_start=12)
    for station in this_stations:
        html = folium.Html(
            f"<a href={url_for('trips.line_info',station_code=station)} target='_top'>{stations[station].name}</a>",
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

def plot_one(station, lines):
    coords = station.coords
    m = folium.Map(location=coords, zoom_start=12)
    for line in lines:
        betweens = []
        for stop in lines[line].stops:
            html = folium.Html(
                f"<a href={url_for('trips.line_info',station_code=stations[stop].code)} target='_top'>{stations[stop].name}</a>",
                script=True,
            )
            betweens.append(stations[stop].coords)
            folium.Marker(
                location=stations[stop].coords,
                popup=folium.Popup(html),
                icon=folium.plugins.BeautifyIcon(icon_shape="circle-dot"),
            ).add_to(m)

        html = folium.Html(
            f"<a href={url_for('trips.line_info',station_code=station.code)} target='_top'>{station.name}</a>",
            script=True,
        )
        folium.Marker(
            location=station.coords,
            popup=folium.Popup(html, show=True),
            icon=folium.plugins.BeautifyIcon(
                icon_shape="doughnut", background_color="black"
            ),
        ).add_to(m)

        folium.PolyLine(betweens, color=lines[line].name, weight=5).add_to(m)

    return m
