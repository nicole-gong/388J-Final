# [CMSC388J](https://aspear.cs.umd.edu/388j) Final Project: UMD(C)

WMATA API PILLLLLL -nicole gong CMSC388j S2024
#### Install the required dependencies:
```console
$ pip3 install -r requirements.txt
```
##### Q1 Description of your final project idea:
WMATA route tracker for metrorails in the DC/MDVA area.

##### Q2 Describe what functionality will only be available to logged-in users:
Users will be able to create itineraries and post them for others to see.

##### Q3 List and describe at least 4 forms:
User Login form
User Registration form
Rail itinerary creation form
Username edit form

##### Q4 List and describe your routes/blueprints (don’t need to list all routes/blueprints you may have–just enough for the requirement):
Main index will be a graph of all train lines. Then detailed information of each individual station. Then user-created itineraries. User index will have login/registration/account view functionality.

##### Q5 Describe what will be stored/retrieved from MongoDB:
I store user account information and the itineraries they create.

##### Q6 Describe what Python package or API you will use and how it will affect the user experience:
I pull information from https://developer.wmata.com/docs/services for real-time incident tracking and general data about rails. I use folium to generate a map of station locations.
