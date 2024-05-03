import requests
import http.client, urllib.request, urllib.parse, urllib.error, base64
from os import getenv
import json
import dateutil
import datetime
from dotenv import load_dotenv
load_dotenv()
headers = {
    "api_key": getenv("WMATA_KEY"),
}

class Trip(object):
    def __init__(self, station_json):
        self.address = station_json["Address"]["Street"]
        self.linecodes = [
            station_json["LineCode1"],
            station_json["LineCode2"],
            station_json["LineCode3"],
        ]
        self.coords = [station_json["Lat"], station_json["Lon"]]
        self.name = station_json["Name"]
        self.code = station_json["Code"]
    def __repr__(self):
        return self.name

class Line(object):
    def __init__(self, json):
        self.LineCode = json["LineCode"]
        self.name = json["DisplayName"]
        self.start = json["StartStationCode"]
        self.end = json["EndStationCode"]
        self.stops = []
    def __repr__(self):
        return self.name

class Distance(object):
    def __init__(self, json):
        self.distance = None
        self.name = json["StationName"]
        self.code = json["StationCode"]
    def __repr__(self):
        return self.distance

class TripClient(object):
    def __init__(self):
        self.sess = requests.Session()

    def display_stations():
        try:
            conn = http.client.HTTPSConnection('api.wmata.com')
            conn.request(
                "GET",
                "https://api.wmata.com/Rail.svc/json/jStations",
                headers=headers,
            )
            response = conn.getresponse()
            data = json.loads(response.read())
            conn.close()
            results = {}
            for station in data["Stations"]:
                results[station["Code"]] = Trip(station)

            return results

        except Exception as e:
            print("[Errno {0}] {1}".format(e.errno, e.strerror))

    def display_lines():
        try:
            conn = http.client.HTTPSConnection('api.wmata.com')
            conn.request(
                "GET",
                "https://api.wmata.com/Rail.svc/json/jLines",
                headers=headers,
            )
            response = conn.getresponse()
            data = json.loads(response.read())
            conn.close()
            lines= {}
            for line in data["Lines"]:
                new_line = Line(line)
                conn = http.client.HTTPSConnection('api.wmata.com')
                conn.request(
                    "GET",
                    f"https://api.wmata.com/Rail.svc/json/jPath?FromStationCode={new_line.start}&ToStationCode={new_line.end}",
                    headers=headers,
                )
                response = conn.getresponse()
                data = json.loads(response.read())
                conn.close()
                for stop in data["Path"]:
                    new_line.stops.append(stop["StationCode"])
                lines[stop["LineCode"]] = new_line

            return lines

        except Exception as e:
            print("[Errno {0}] {1}".format(e.errno, e.strerror))

    def display_station(code):
        try:
            conn = http.client.HTTPSConnection('api.wmata.com')
            conn.request(
                "GET",
                f"https://api.wmata.com/Rail.svc/json/jStationInfo?StationCode={code}",
                headers=headers,
            )
            response = conn.getresponse()
            data = json.loads(response.read())
            conn.close()
            return Trip(data)

        except Exception as e:
            print("[Errno {0}] {1}".format(e.errno, e.strerror))

    def shortest_path(src, dest):
        conn = http.client.HTTPSConnection('api.wmata.com')
        conn.request(
            "GET",
            f"https://api.wmata.com/Rail.svc/json/jPath?FromStationCode={src}&ToStationCode={dest}",
            headers=headers,
        )
        response = conn.getresponse()
        data = json.loads(response.read())
        conn.close()
        distance = 0
        results = []
        for station in data["Path"][1:]:
            distance += station["DistanceToPrev"]
            new_distance = Distance(station)
            new_distance.distance = distance
            results.append(new_distance)
        return results
