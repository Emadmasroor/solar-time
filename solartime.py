'''
This script calculates the "solar time" of the current location
by making use of the current time in UTC. It basically measures
how far from sunrise we currently are and then calculates what the
time would be if we assumed that 6:00 AM was sunrise and 6:00 PM
was sunset.

It also calculates the solar time making use of the sun's current
altitude, as well as the altitude at solar noon at this location
and at this day. 

'''

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
current_time = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)


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
nadir_here      = key_times["solar_nadir"]

# During the day:
time_since_sunrise = current_time - sunrise_here
length_day = sunset_here - sunrise_here
length_second = length_day.seconds/(12*60*60)

# During the night:
time_since_sunset = current_time - sunset_here
length_night = (key_times["sunrise"] - key_times["sunset"]) % dt.timedelta(days=1)
length_second_night = length_night.seconds/(12*60*60)



# Fraction of the solar day that has passed.
fractional_time = time_since_sunrise.seconds/length_day.seconds

fractional_day_time = (fractional_time * 12 + 6) # count from 6 AM sunrise.

tt = dt.timedelta(hours=fractional_day_time).seconds
h = tt // 3600
m = (tt % 3600) // 60
s = (tt % 60)

# Fraction of the solar night that has passed.
fractional_time_night = time_since_sunset.seconds/length_night.seconds



# Some info about the day here
# print(f"We are in {geocoder.ip('me').current_result}")
print(f"The day is {length_day.seconds//60} minutes long.")
print(f"Each second of UTC solar day time is {length_second:.3f} seconds long on the clock.")
print(f"We are currently {time_since_sunrise.seconds//60} minutes from sunrise.")
print(f"1-fractionally, {fractional_time:.3f} of the day has passed")
print(f"{fractional_time * 12 :.3f} hours out of 12 hours of the day have passed")
print(f"So the UTC solar day time is {h:02d}:{m:02d}:{s:02d}")
print("")

# Find out how high the sun is today at solar noon.
highest_altitude_today = degrees(get_position(noon_here, lon, lat)["altitude"])
print(f"At solar noon, the sun would be {highest_altitude_today:.1f} degrees high in the sky")

# Print current altitude of the sun.
print(f"The sun is currently {alt:.1f} degrees high in the sky.")

# Sunrise is 0 degrees and sunset is 180 degrees. Locate the sun from 0 to 180.
if current_time < noon_here:
    degrees_from_sunrise = alt/highest_altitude_today * 90
    print("Noon has not occurred yet.")
else:
    degrees_from_noon = (highest_altitude_today - alt)/highest_altitude_today * 90
    degrees_from_sunrise = degrees_from_noon + 90
    print("It is past noon.")

# Print fractional solar path
print(f"The sun is {(degrees_from_sunrise):.1f}/180 degrees of the way to sunset.")

h_s = int(degrees_from_sunrise / 15) + 6
m_s = int(((degrees_from_sunrise % 15)/15)*60)
s_s = int(((degrees_from_sunrise % 15)/15)*60 % 1 * 60)

print(f"So the altitudinal solar time is {h_s:02d}:{m_s:02d}:{s_s:02d}")

# Assemble the times
line3 = f"{h_s:02d}:{m_s:02d}:{s_s:02d}"
line2 = f"{h:02d}:{m:02d}:{s:02d}"
line1 = f"{h1:02d}:{m1:02d}:{s1:02d}"

clock_time = dt.time(h1,m1,s1)
solar_time = dt.time(h_s,m_s,s_s)

# Figure

fig = graphs.Figure(graphs.Indicator(
    domain = {'x': [0, 1], 'y': [0, 1]},
    value = degrees_from_sunrise,
    mode = "gauge",
    title = {'text': "Altitudinal Solar Time"},
    gauge = {'axis':
             {
                'range': [0, 180],
                'tickvals': list(range(0,181,15)),
                'ticktext': [f"{6+val//15}:00" for val in range(0,181,15)],
                'tickfont': {'size': 16, 'family': 'Arial'},
                'tickwidth': 2,
                'tickcolor': "black"
                
              },
             'steps' : [{'range': [0, 180], 'color': "lightgray"}],
             'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 150}}
    )
    )

fig.add_annotation(
    text=f"<span style='font-size:36px; font-weight:bold;'>Clock Time {line1}</span><br>"
         f"<span style='font-size:36px; color:gray;'>UTC Solar Time {line2}</span><br>"
         f"<span style='font-size:36px; color:green; font-weight:bold;'>True Solar Time {line3}</span>",
    # text=f"<b>{h:02d}:{m:02d}:{s:02d}</b>", # Using HTML <b> tag to make it bold
    x=0.5, 
    y=0.2,             # Coordinates relative to the canvas (0 to 1)
    xref="paper",
    yref="paper",
    font=dict(size=48, color="black", family="Arial"),
    showarrow=False     # Removes the pointer arrow
)

fig.show()
