from suncalc import get_position, get_times
import datetime as dt
from math import degrees
import plotly.graph_objects as graphs
import streamlit as st
import time

def get_time_stretch(lat, lon, at_time=None):
    if at_time is None:
        at_time = dt.datetime.now()
    # Calculates the stretch at the time given by at_time
    # by adding one second and looking at the difference
    solartime_0 = get_solar_time(lat, lon, at_time)
    solartime_1 = get_solar_time(lat, lon, at_time + dt.timedelta(seconds=1))
    
    ratio = 1 / ((solartime_1.second + 1e-6 * solartime_1.microsecond) - (solartime_0.second + 1e-6 * solartime_0.microsecond))
    return ratio

def get_solar_time(lat, lon, current_time_local=None):
    if current_time_local is None:
        current_time_local = dt.datetime.now()
        
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

    if alt > 0:
        # it is day time.
        if azm < 0:
            degrees_from_sunrise = alt/highest_altitude_today * 90
        else:
            degrees_from_noon   = (highest_altitude_today - alt)/highest_altitude_today * 90
            degrees_from_sunrise= degrees_from_noon + 90
        fractional_time_hours   = degrees_from_sunrise/15 + 6
    else:
        # it is night time.
        if azm > 0:
            degrees_from_sunset = alt/lowest_altitude_today * 90
        else:
            degrees_from_nadir  = (lowest_altitude_today - alt)/lowest_altitude_today
            degrees_from_sunset = degrees_from_nadir + 90
        fractional_time_hours   = degrees_from_sunset/15 + 18

    # Solar time in hours, minutes and seconds.
    total_seconds = dt.timedelta(hours=fractional_time_hours).seconds
    h_s, remainder = divmod(total_seconds, 3600)
    m_s, s_s = divmod(remainder, 60)
    ms_s = dt.timedelta(hours=fractional_time_hours).microseconds

    solar_time = dt.time(h_s, m_s, s_s, ms_s)
    return solar_time

def show_solar_time(lat, lon, solartime, clocktime):
    line1 = clocktime.strftime("%H:%M:%S.%f")[:-4]
    line2 = solartime.strftime("%H:%M:%S.%f")[:-4]
    line3 = f"1 clock sec = {get_time_stretch(lat, lon, clocktime):.2f} solar sec"
    
    degrees_from_sunrise = (-6 + solartime.hour + solartime.minute/60 + solartime.second/3600)/12 * 180

    fig = graphs.Figure(
        data=graphs.Scatterpolar(
            r=[0, 1],
            theta=[2, 180-degrees_from_sunrise],
            mode='markers+lines',
            marker=dict(color='darkorange', size=[0, 20]),
            line=dict(color='black', width=1)
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
                gridcolor="rgba(0, 0, 0, 0.05)",
                gridwidth=1
            )
        )
    )

    fig.add_annotation(
        text=f"<div style='line-height: 1.1; text-align: center;'>"
             f"<span style='font-size:18px; color:gray; font-weight:bold;'>Clock Time {line1}</span><br>"
             f"<span style='font-size:18px; color:green; font-weight:bold'>Solar Time {line2}</span><br>"
             f"<span style='font-size:14px; color:teal; font-weight:bold'>{line3}</span>"
             f"</div>",
        x=0.5, 
        y=1.35,
        xref="paper",
        yref="paper",
        font=dict(family="Courier"),
        showarrow=False
    )

    return fig


# --- Streamlit UI Setup ---
st.set_page_config(page_title="Interactive Solar Time", layout="centered")

# 1. Add interactive input widgets to a clean sidebar
st.sidebar.header("Location Settings")
st.sidebar.markdown("Enter your coordinates to recalculate solar time.")

# We use number_input so the user can freely type or step through coordinates.
# Defaults are set to Philadelphia.
user_lat = st.sidebar.number_input("Latitude", min_value=-90.0, max_value=90.0, value=39.9524, format="%.4f")
user_lon = st.sidebar.number_input("Longitude", min_value=-180.0, max_value=180.0, value=-75.1636, format="%.4f")

st.title("Local Solar Time Dial")
st.markdown(f"**Current Tracking Location:** {user_lat:.4f}°, {user_lon:.4f}°")

# 2. Calculate times based on the user's input
set_time = dt.datetime.now()
sol_time = get_solar_time(user_lat, user_lon, set_time)
figure = show_solar_time(user_lat, user_lon, sol_time, set_time)

# 3. Render the Plotly chart natively (no placeholder block needed anymore)
st.plotly_chart(figure, use_container_width=True)

# 4. The Native Streamlit Refresh Loop
# Wait 10 seconds, then safely restart the script to pull fresh time and new inputs
time.sleep(10)
st.rerun()
