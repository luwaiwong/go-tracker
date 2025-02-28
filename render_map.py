import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import numpy as np
import datetime

import requests
import config

# OPTIONS
SHOW_ONLY_TRAINS = True

# CONSTANTS
DEFAULT_CENTER = {"lat": 43.651070, "lon": -79.347015}  # Toronto
DEFAULT_ZOOM = 10

base_url = "https://api.openmetrolinx.com/OpenDataAPI/"
api_key = "?key="+config.API_KEY
train_position_api = "api/V1/Gtfs/Feed/VehiclePosition/"

def get_stop_details():
    # Open CSV
    stations = pd.read_json("./station_details.json")

    lats = []
    lons = []
    names = []
    types = []
    # Create list of station locations
    for ids, data in stations.items():
        info = data.get("Stop", {})

        name = info.get("StopName")
        lon, lat = info.get("Longitude"), info.get("Latitude")
        is_train = info.get("IsTrain")
        
        if SHOW_ONLY_TRAINS and not is_train:
            continue

        if lon and lat:
            lats.append(float(lat))
            lons.append(float(lon))
            names.append(name)
            types.append("station")
    return lats, lons, names, types

def get_trains():
    lats = []
    lons = []
    names = []
    types = []

    try:
        response = requests.get(base_url+train_position_api+api_key)
        if response.status_code == 200:
            data = response.json()

            for vehicle in data["entity"]:
                info = vehicle["vehicle"]  
                position = info["position"]
                name = info["vehicle"]["label"]
                stop_id = info["stop_id"]
                
                # Add info
                if (stop_id.isdigit()):
                    # continue
                    types.append("bus")
                else:
                    types.append("train")
                lats.append(position["latitude"])
                lons.append(position["longitude"])
                names.append(name)
        else:
            print('Error:', response.status_code)
    except requests.exceptions.RequestException as e:
        print('Error:', e)
    
    return lats, lons, names, types


########## APP INITILIZATION ##########
s_lats, s_lons, s_names, s_types = get_stop_details()

app = dash.Dash(__name__)

# Define Layout of the app
app.layout = html.Div([
    dcc.Graph(id='live-update-map', style={'height': '100vh'}),
    dcc.Interval(
        id='interval-component',
        interval=1*1000,  # Update every second
        n_intervals=0
    )
])

# Callback to update the map without resetting zoom
@app.callback(
    Output('live-update-map', 'figure'),
    Input('interval-component', 'n_intervals'),
    State('live-update-map', 'figure')  # Preserve previous state
)
def update_map(n, prev_figure):
    # Get train locations
    t_lats, t_lons, t_names, t_types = get_trains()

    # Gather data
    lats = s_lats+t_lats
    lons = s_lons+t_lons
    names = s_names+t_names
    types = s_types+t_types
    # lats = t_lats
    # lons = t_lons
    # names = t_names
    # types = t_types


    # Condense data for map
    data = pd.DataFrame({
        'Latitude': lats,
        'Longitude': lons,
        'Name': names,
        'Type': types
    })

    # Create the map figure
    fig = px.scatter_map(
        data,
        lat='Latitude',
        lon='Longitude',
        hover_name='Name',
        zoom=DEFAULT_ZOOM,
        center=DEFAULT_CENTER,
        color = 'Type',
    )

    # Preserve previous zoom and center if available
    if prev_figure:
        fig.update_layout(
            map=dict(
                center=prev_figure['layout']['map'].get('center', DEFAULT_CENTER),
                zoom=prev_figure['layout']['map'].get('zoom', DEFAULT_ZOOM)
            )
        )

    fig.update_layout(
        mapbox_style="open-street-map",
        title='Real-Time Updating Map'
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
