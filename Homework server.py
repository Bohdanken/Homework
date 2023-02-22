import datetime as dt
import json

import requests
from flask import Flask, jsonify, request

import datetime as dt
import json

import requests
from flask import Flask, jsonify, request
import csv
import codecs
import urllib.request
import urllib.error
import sys
from datetime import datetime, timezone

# create your API token, and set it up in Postman collection as part of the Body section
API_TOKEN = "ssg"
ApiKey = 'HQFGAECMBY828ETKESEMCPBP6'

# include sections
# values include days,hours,current,alerts
Include = "days"

app = Flask(__name__)


def generate_forecast(Location, StartDate, EndDate):
    BaseURL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
    # "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/[location]/[date1]/[date2]?key=YOUR_API_KEY"
    ContentType = "json"
    UnitGroup = "metric"
    Include = "days"
    # basic query including location
    ApiQuery = BaseURL + Location

    # append the start and end date if present
    if (len(StartDate)):
        ApiQuery += "/" + StartDate
        if (len(EndDate)):
            ApiQuery += "/" + EndDate

    # Url is completed. Now add query parameters (could be passed as GET or POST)
    ApiQuery += "?"

    # append each parameter as necessary
    if (len(UnitGroup)):
        ApiQuery += "&unitGroup=" + UnitGroup

    if (len(ContentType)):
        ApiQuery += "&contentType=" + ContentType

    if (len(Include)):
        ApiQuery += "&include=" + Include

    ApiQuery += "&key=" + ApiKey
    CSVBytes = None
    try:
        CSVBytes = urllib.request.urlopen(ApiQuery)
    except urllib.error.HTTPError as e:
        ErrorInfo = e.read().decode()
        print('Error code: ', e.code, ErrorInfo)
        sys.exit()
    except  urllib.error.URLError as e:
        ErrorInfo = e.read().decode()
        print('Error code: ', e.code, ErrorInfo)
        sys.exit()


    return CSVBytes


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>ss2</h2></p>"


@app.route(
    "/content/api/v1/integration/generate",
    methods=["POST"],
)
def endpoint():
    start_dt = datetime.now(timezone.utc)
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    token = json_data.get("token")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    requester_name = ""
    if json_data.get("requester_name"):
        requester_name = json_data.get("requester_name")
    location = ""
    if json_data.get("location"):
        location = json_data.get("location")
    start_date = ""
    if json_data.get("start_date"):
        start_date = json_data.get("start_date")
    end_date = ""
    if json_data.get("end_date"):
        end_date = json_data.get("end_date")

       # json.loads(Bytes)
    forecast = generate_forecast(location, start_date, end_date)
    data = json.load(forecast)
    if data.get("days"):
        info = data.get("days")
    else: info = "No data"
    result = {
        "requester_name": requester_name,
        "timestamp": start_dt,
        "location": location,
        "days": start_date+":"+end_date,
         "weather": info

    }

    return result