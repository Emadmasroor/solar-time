from suncalc import get_position, get_times
import datetime as dt
import geocoder
# from zoneinfo import ZoneInfo
from math import degrees
import plotly.graph_objects as graphs


# Calculate current length of a minute
def get_time_stretch(at_time = dt.datetime.now()):
    # Calculates the stretch at the time given by at_time
    # by adding one second and looking at the difference

    solartime_0 = get_solar_time(at_time)
    solartime_1 = get_solar_time(at_time+dt.timedelta(seconds=1))
    
    ratio = 1 / ((solartime_1.second + 1e-6 * solartime_1.microsecond) - (solartime_0.second + 1e-6 * solartime_0.microsecond))

    return ratio

# Get current GPS coordinates - use sparingly!

##lat = 39.952
##lon = -75.163
def get_my_coordinates():
    try:
        [lat, lon] = geocoder.ip('me').latlng
        return lat, lon
    except Exception:
        return 39.952,-75.163

def get_solar_time(current_time_local = dt.datetime.now()):
    # Calculates the solar time and returns it as a date-time object.

    lat, lon = get_my_coordinates()
    
    # Get sun's current position
    sun_position = get_position(current_time_local, lon, lat)
    alt = degrees(sun_position["altitude"])
    azm = degrees(sun_position["azimuth"])

    # Get some info about this location
    key_times = get_times(current_time_local, lon, lat)

    sunrise_here    = key_times["sunrise"]
    sunset_here     = key_times["sunset"]
    noon_here       = key_times["solar_noon"]
    nadir_here      = key_times["nadir"]

    highest_altitude_today = degrees(get_position(noon_here, lon, lat)["altitude"])
    lowest_altitude_today  = degrees(get_position(nadir_here, lon, lat)["altitude"])

    if alt > 0 :
        # it is day time.
        length_day = sunset_here - sunrise_here
        length_second_day = length_day.seconds/(12*60*60)
        if azm < 0:
            # i.e., check if we are in the 6 AM - 12 PM period.
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
        length_night = (key_times["sunrise"] - key_times["sunset"]) % dt.timedelta(days=1)
        length_second_night = length_night.seconds/(12*60*60)
        if azm > 0:
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

    return solar_time


set_time = dt.datetime.now() + dt.timedelta(hours=8)


stobj = get_solar_time(current_time_local = set_time)
degrees_from_sunrise = (-6 + stobj.hour + stobj.minute/60 + stobj.second/3600)/12 * 180
line2 = stobj.strftime("%H:%M:%S.%f")[:-4]
line1 = set_time.strftime("%H:%M:%S.%f")[:-4] # calling it this way ensures it's not in UTC but in correct time zone.
line3 = f"1 clock sec = {get_time_stretch(set_time):.2f} solar sec"

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
    )
)

fig.add_annotation(
    text=f"<span style='font-size:18px; color:gray; font-weight:bold;'>Clock Time {line1}</span><br>"
         f"<span style='font-size:18px; color:green; font-weight:bold'>Solar Time {line2}</span><br>"
         f"<span style='font-size:14px; color:teal; font-weight:bold'>{line3}</span><br>",
    # text=f"<b>{h:02d}:{m:02d}:{s:02d}</b>", # Using HTML <b> tag to make it bold
    x=0.5, 
    y=1.2,             # Coordinates relative to the canvas (0 to 1)
    xref="paper",
    yref="paper",
    font=dict(family="Courier"),
    showarrow=False     # Removes the pointer arrow
)
fig.show()
