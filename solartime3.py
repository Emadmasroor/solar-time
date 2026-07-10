from suncalc import get_position, get_times
import datetime as dt
import geocoder
# from zoneinfo import ZoneInfo
from math import degrees
import plotly.graph_objects as graphs

# Get current GPS coordinates - use sparingly!

# [lat, lon] = geocoder.ip('me').latlng
[lat, lon] = [39.9524, -75.1636]

# Get current time in UTC, then strip away time zone info. All times are always in UTC.
current_time = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None) # for debugging

# Get local time
t1 = dt.datetime.now()
h1 = t1.hour
m1 = t1.minute
s1 = t1.second


# Get sun's current position
sun_position = get_position(dt.datetime.now(), lon, lat)
alt = degrees(sun_position["altitude"])
azm = degrees(sun_position["azimuth"])

# Get some info about this location
key_times = get_times(current_time, lon, lat)

sunrise_here    = key_times["sunrise"]
sunset_here     = key_times["sunset"]
noon_here       = key_times["solar_noon"]
nadir_here      = key_times["nadir"]

highest_altitude_today = degrees(get_position(noon_here, lon, lat)["altitude"])
lowest_altitude_today  = degrees(get_position(nadir_here, lon, lat)["altitude"])


if current_time > sunrise_here:
    # it is day time.
    time_since_sunrise = current_time - sunrise_here
    length_day = sunset_here - sunrise_here
    length_second_day = length_day.seconds/(12*60*60)
    if current_time < noon_here:
        # i.e., check if we are in the 6 AM - 12 PM period
        degrees_from_sunrise = alt/highest_altitude_today * 90
    else:
        # i.e., check if we are in the 12 PM - 6 PM period
        degrees_from_noon   = (highest_altitude_today - alt)/highest_altitude_today * 90
        degrees_from_sunrise= degrees_from_noon + 90
    # fractional_time = time_since_sunrise.seconds/length_day.seconds * 0.5
    fractional_time_hours   = degrees_from_sunrise/15 + 6
    fractional_time         = dt.timedelta(hours=fractional_time_hours)
else:
    # it is night time.
    time_since_sunset = current_time - sunset_here
    length_night = (key_times["sunrise"] - key_times["sunset"]) % dt.timedelta(days=1)
    length_second_night = length_night.seconds/(12*60*60)
    if current_time < nadir_here:
        # check if we are in the 6 PM - 12 AM period
        degrees_from_sunset = alt/lowest_altitude_today * 90
    else:
        # check if we are in the 12 AM - 6 AM period
        degrees_from_nadir  = (lowest_altitude_today - alt)/lowest_altitude_today
        degrees_from_sunset = degrees_from_nadir + 90
    fractional_time_hours   = degrees_from_sunset/15 + 18
    fractional_time         = dt.timedelta(hours=fractional_time_hours)

# Solar time in hours, minutes and seconds.
total_seconds = dt.timedelta(hours=fractional_time_hours).seconds

h_s, remainder = divmod(total_seconds, 3600)
m_s, s_s = divmod(remainder, 60)
ms_s =dt.timedelta(hours=fractional_time_hours).microseconds

solar_time = dt.time(h_s,m_s,s_s,ms_s)

print(solar_time.strftime("%H:%M:%S.%f")[:-4])
