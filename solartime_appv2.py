from suncalc import get_position, get_times
import datetime as dt
import geocoder
# from zoneinfo import ZoneInfo
from math import degrees
import plotly.graph_objects as graphs
import streamlit as st
import time
# pip install pyobjc-framework-CoreLocation
# from CoreLocation import CLLocationManager

# Get location once at startup
# @st.cache_data
def get_my_coordinates():
    try:
        # [lat, lon] = geocoder.ip('me').latlng
        lat = 39.952
        lon = -75.163
        return lat, lon
    except Exception:
        # Fallback coordinates (e.g., NYC) if the API fails or rate limits you
        return 39.9524, -75.1636 # Philadelphia

def get_solar_time():
    
    # Get current GPS coordinates
    # [lat, lon] = geocoder.ip('me').latlng
    
    lat, lon = get_my_coordinates()

    # Get current time in UTC, then strip away time zone info. All times are always in UTC.
    current_time = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)

    # Get local time
    t1 = dt.datetime.now()
    h1 = t1.hour
    m1 = t1.minute
    s1 = t1.second
    ms1= t1.microsecond

    # Get sun's current position
    sun_position = get_position(dt.datetime.now(), lon, lat)
    alt = degrees(sun_position["altitude"])
    azm = degrees(sun_position["azimuth"])

    # Get some info about this location
    key_times = get_times(current_time, lon, lat)

    sunrise_here    = key_times["sunrise"]
    sunset_here     = key_times["sunset"]
    noon_here       = key_times["solar_noon"]

    time_since_sunrise = current_time - sunrise_here
    length_day = sunset_here - sunrise_here
    length_second = length_day.seconds/(12*60*60)

    # Find out how high the sun is today at solar noon.
    highest_altitude_today = degrees(get_position(noon_here, lon, lat)["altitude"])

    # Sunrise is 0 degrees and sunset is 180 degrees. Locate the sun from 0 to 180.
    if current_time < noon_here:
        degrees_from_sunrise = alt/highest_altitude_today * 90
    else:
        degrees_from_noon = (highest_altitude_today - alt)/highest_altitude_today * 90
        degrees_from_sunrise = degrees_from_noon + 90

    h_s = int(degrees_from_sunrise / 15) + 6
    m_s = int(((degrees_from_sunrise % 15)/15)*60)
    s_s = int(((degrees_from_sunrise % 15)/15)*60 % 1 * 60)
    ms_s= int((((degrees_from_sunrise % 15)/15)*60 % 1 * 60) % 1 * 1e6)

    # Assemble the times
    # line3 = f"{h_s:02d}:{m_s:02d}:{s_s:02d}.{ms_s:.2f}"
    # line1 = f"{h1:02d}:{m1:02d}:{s1:02d}.{ms1:.2f}"

    clock_time = dt.time(h1,m1,s1,ms1)
    solar_time = dt.time(h_s,m_s,s_s,ms_s)
    
    return solar_time

def show_solar_time(stobj):
    degrees_from_sunrise = (-6 + stobj.hour + stobj.minute/60 + stobj.second/3600)/12 * 180
    line2 = stobj.strftime("%H:%M:%S.%f")[:-4]
    line1 = dt.datetime.now().strftime("%H:%M:%S.%f")[:-4]
    
    fig = graphs.Figure(
        data = graphs.Scatterpolar(
            r = [0,1],
            theta = [2, 180-degrees_from_sunrise],
            mode = 'markers+lines',
            marker=dict(
                color='darkorange',  # Bright orange filled circle
                size=[0,20]                 # Bigger size
                ),
            line=dict(
            color='black',
            width=1
                )
            )
        )

    fig.update_layout(
        showlegend=False,
        polar=dict(
            radialaxis=dict(visible=False),
            angularaxis=dict(
                tickvals=list(range(0, 361, 15)),
                ticktext=[f"{(-(val//15) + 18) % 24}:00" for val in range(0, 361, 15)],
                tickfont=dict(size=16, family="Arial"),
                gridcolor="rgba(0, 0, 0, 0.05)",  # Makes the radial lines very faint
                gridwidth=1
            )
        ),
        template="plotly_white",
        polar_sectors=[
            dict(theta=[0, 90], fillcolor="rgba(230, 242, 255, 0.4)", line_width=0),   # Quad 1 (Light Blue)
            dict(theta=[90, 180], fillcolor="rgba(230, 255, 230, 0.4)", line_width=0),  # Quad 2 (Light Green)
            dict(theta=[180, 270], fillcolor="rgba(255, 255, 230, 0.4)", line_width=0), # Quad 3 (Light Yellow)
            dict(theta=[270, 360], fillcolor="rgba(255, 230, 230, 0.4)", line_width=0)  # Quad 4 (Light Red)
        ]
    )
    return fig

##solar_time_obj = get_solar_time()
##show_solar_time(solar_time_obj).show()

# Streamlit
st.set_page_config(page_title="Solar Time Gauge", layout="centered")
st.title("Solar Time in Philadelphia")

# --- The Streamlit Loop ---

# 1. Create a dedicated placeholder layout block on the page
gauge_container = st.empty()

# 2. Run the update engine endlessly
while True:
    # Recalculate everything
    solar_time_obj = get_solar_time()
    figure = show_solar_time(solar_time_obj)
    
    # Render the new figure directly inside our placeholder block
    gauge_container.plotly_chart(figure, width=800)
    
    # 3. Tell Python to wait 2 seconds before executing the loop again
    time.sleep(1)

