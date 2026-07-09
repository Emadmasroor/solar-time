from suncalc import get_position, get_times
import datetime as dt
import geocoder
# from zoneinfo import ZoneInfo
from math import degrees
import plotly.graph_objects as graphs

def get_solar_time():
    
    # Get current GPS coordinates
    [lat, lon] = geocoder.ip('me').latlng

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
    line3 = f"{h_s:02d}:{m_s:02d}:{s_s:02d}"
    line1 = f"{h1:02d}:{m1:02d}:{s1:02d}"

    clock_time = dt.time(h1,m1,s1,ms1)
    solar_time = dt.time(h_s,m_s,s_s,ms_s)
    
    return solar_time
