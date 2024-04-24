import requests
# import googlemaps
import http.client, urllib.request, urllib.parse, urllib.error, base64

import json
import dateutil
import datetime

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

class TripClient(object):
    def __init__(self):
        self.sess = requests.Session()

    def display_all():
        headers = {
            # Request headers
            "api_key": "cc24d47f8cc24cf2a6ad15961ff446d2",
        }

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
            results, lines = {}, []
            for station in data["Stations"]:
                results[station["Code"]] = Trip(station)
            
            conn = http.client.HTTPSConnection('api.wmata.com')
            conn.request(
                "GET",
                "https://api.wmata.com/Rail.svc/json/jLines",
                headers=headers,
            )
            response = conn.getresponse()
            data = json.loads(response.read())
            conn.close()
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
                lines.append(new_line)

            return {"stations": results, "lines": lines}

        except Exception as e:
            print("[Errno {0}] {1}".format(e.errno, e.strerror))

# class api(object):
#     def __init__(self, api_key):
#         self.session = requests.Session()
#         self.key = api_key
#         self.client = googlemaps.Client(self.key)

#     """
#     uses google maps python api to find address data for a place input as a string,
#     returns the address from the response, if an error occurs, prints code and message
#     associated with the error type
#     """
#     def get_addr(self, location):
#         query = f'Closest Metro Station to {location} Washington DC'
#         response = json.load(self.client.find_place(input=query,
#                                                   input_type='textquery',
#                                                   fields=['formatted_address','name']))
#         if "error" in response:
#             code = response["error"]["code"]
#             msg = response["error"]["message"]
#             return f'Code:{code}, Error Message: {msg}'

#         return response['candidates'][0]['formatted_address']

#     """
#     queries a route from the google routes api between point start and point end,
#     if an error occurs, prints the code and message associated with the error type
#     """
#     def compute_route(self, start, end, departure_t):
#         routes_url = "https://routes.googleapis.com/directions/v2:computeRoutes"

#         # get addresses of start and end
#         origin_addr = self.get_addr(location=start)
#         dest_addr = self.get_addr(location=end)

#         # format data to pass into request
#         headers = {
#             'Content-Type': 'application/json',
#             'X-Goog-Api-Key': self.key,
#             'X-Goog-FieldMask': 'routes.legs.steps.transitDetails'
#         }

#         # extra parameters for query
#         data = {
#             "origin" : {
#                 "address": origin_addr
#             },
#             "destination": {
#                 "address": dest_addr
#             },
#             'travelMode': "TRANSIT",
#             'departureTime': departure_t,
#             'transitPreferences': {
#                 'allowedTravelModes': ["SUBWAY", "TRAIN"]
#             }
#         }

#         # request
#         response = requests.post(routes_url, headers=headers, json=data)

#         if "error" in response:
#             code = response["error"]["code"]
#             msg = response["error"]["message"]
#             return f'Code:{code}, Error Message:{msg}'

#         return response
