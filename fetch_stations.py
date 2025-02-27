import requests
import config
import json

base_url = "https://api.openmetrolinx.com/OpenDataAPI/"
api_key = "?key="+config.API_KEY
all_stops_api = "api/V1/Stop/All/"
stop_detail_api = "api/V1/Stop/Details/"


# Get All Stops
def get_all_stops():
    try:
        response = requests.get(base_url+all_stops_api+api_key)
        if response.status_code == 200:
            data = response.json()
            stop_ids = data.get("Stations")["Station"]
            return stop_ids
        else:
            print('Error:', response.status_code)
    except requests.exceptions.RequestException as e:
        print('Error:', e)
    exit

def get_stop_detail(stop_code):
    try:
        response = requests.get(base_url+stop_detail_api+stop_code+api_key)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print('Error:', response.status_code)
    except requests.exceptions.RequestException as e:
        print('Error:', e)
    exit

def record_all_stops():
    stop_ids = get_all_stops()
    stop_details = {}
    for id in stop_ids:
        code = id["LocationCode"]
        stop = get_stop_detail(code)
        print(stop)
        stop_details[code] = stop
    
    # Write JSON data
    with open('station_details.json', 'w') as fp:
        json.dump(stop_details, fp, indent = 4) 

record_all_stops()