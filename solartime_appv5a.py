from suncalc import get_position, get_times
import datetime as dt
from math import degrees
import plotly.graph_objects as graphs
import streamlit as st
import time
from zoneinfo import ZoneInfo
from timezonefinder import timezone_at

def get_time_stretch(lat, lon, at_time=None):
    if at_time is None:
        at_time = dt.datetime.now()
    # Calculates the stretch at the time given by at_time
    # by adding one second and looking at the difference
    solartime_0 = get_solar_time(lat, lon, at_time)
    solartime_1 = get_solar_time(lat, lon, at_time + dt.timedelta(seconds=1))
    
    ratio = 1 / ((solartime_1.second + 1e-6 * solartime_1.microsecond) - (solartime_0.second + 1e-6 * solartime_0.microsecond))
    return ratio

def get_local_time_from_coords(lat,lon):
    # Uses lat and lon to determine correct time zone
    # then uses datetime to get the current time in this time zone.

    return dt.datetime.now(ZoneInfo(timezone_at(lng=lon,lat=lat)))

    
    
    
    

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
            # 6 AM to 12 PM
            degrees_from_sunrise = alt/highest_altitude_today * 90
        else:
            # 12 PM to 6 PM
            degrees_from_noon   = (highest_altitude_today - alt)/highest_altitude_today * 90
            degrees_from_sunrise= degrees_from_noon + 90
        fractional_time_hours   = degrees_from_sunrise/15 + 6
    else:
        # it is night time.
        if azm > 0:
            # 6 PM to 12 AM
            degrees_from_sunset = alt/lowest_altitude_today * 90
        else:
            # 12 AM to 6 AM
            degrees_from_nadir  = (lowest_altitude_today - alt)/lowest_altitude_today * 90
            degrees_from_sunset = degrees_from_nadir + 90
        fractional_time_hours   = (degrees_from_sunset/15 + 18) % 24

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

    # --- 1. Define the 4 Faint Background Sectors ---
    # We use rgba() colors with a very low decimal at the end (alpha) for transparency
    
    sector_afternoon = graphs.Scatterpolar(
        r=[0, 1, 1, 0], theta=[0, 0, 90, 90],
        fill="toself", fillcolor="rgba(255, 195, 0, 0.12)",  # Soft Golden Orange
        mode="none", showlegend=False
    )
    
    sector_morning = graphs.Scatterpolar(
        r=[0, 1, 1, 0], theta=[90, 90, 180, 180],
        fill="toself", fillcolor="rgba(255, 240, 150, 0.18)",  # Faint Morning Yellow
        mode="none", showlegend=False
    )
    
    sector_night = graphs.Scatterpolar(
        r=[0, 1, 1, 0], theta=[180, 180, 270, 270],
        fill="toself", fillcolor="rgba(100, 110, 240, 0.12)",  # Deep Midnight Blue
        mode="none", showlegend=False
    )
    
    sector_evening = graphs.Scatterpolar(
        r=[0, 1, 1, 0], theta=[270, 270, 360, 360],
        fill="toself", fillcolor="rgba(30, 144, 255, 0.12)",  # Twilight Blue
        mode="none", showlegend=False
    )

    # --- 2. The Clock Hand ---
    clock_hand = graphs.Scatterpolar(
        r=[0, 1],
        theta=[2, 180-degrees_from_sunrise],
        mode='markers+lines',
        marker=dict(color='darkorange', size=[0, 20]),
        line=dict(color='black', width=2)  # Bumped to width=2 to make the hand pop out
    )

    # --- 3. Assemble the Figure ---
    # The order here is critical: background shapes go first, hand goes last
    fig = graphs.Figure(data=[sector_afternoon, sector_morning, sector_night, sector_evening, clock_hand])

    fig.update_layout(
        showlegend=False,
        polar=dict(
            radialaxis=dict(visible=False, range=[0, 1]),  # Ensures the background fills the entire radius ring uniformly
            angularaxis=dict(
                tickvals=list(range(0, 361, 15)),
                ticktext=[f"{(-(val//15) + 18) % 24}:00" for val in range(0, 361, 15)],
                tickfont=dict(size=16, family="Arial"),
                gridcolor="rgba(0, 0, 0, 0.08)",  # Darkened grid slightly so it cuts cleanly through the shadings
                gridwidth=1
            )
        )
    )

    fig.add_annotation(
        text=f"<span style='font-size:18px; color:gray; font-weight:bold;'>Clock Time {line1}</span><br>"
             f"<span style='font-size:18px; color:green; font-weight:bold'>Solar Time {line2}</span><br>"
             f"<span style='font-size:14px; color:teal; font-weight:bold'>{line3}</span>",
        x=0.5, 
        y=1.35,
        xref="paper",
        yref="paper",
        font=dict(family="Courier"),
        showarrow=False
    )

    return fig

# --- Streamlit UI Setup ---
st.set_page_config(page_title="Interactive Solar Time", layout="wide")
st.title("Solar Clock")

# Create the two main panel columns (1 part text panel, 2 parts visualization panel)
col1, col2 = st.columns([1, 2])

# PANEL 2: Left column handles the stacked layout (Plot first, Inputs second)
with col1:
    # Reserve the top of column 2 for the plot layout slot
    plot_slot = st.container()
    
    st.write("---")
    st.subheader("Location")
    
    # Nested side-by-side inputs to look neat under the plot
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        user_lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=39.9524, format="%.4f")
    with sub_col2:
        user_lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=-75.1636, format="%.4f")
        
    st.markdown(f"**Detected Timezone**: {timezone_at(lng=user_lon, lat=user_lat)}")
    st.caption("Philadelphia is roughly (40, -75).")


# PANEL 1: Right column handles your long text descriptions
with col2:
    st.subheader("About Solar Time")
    st.markdown("Traditional clocks don't make sense. Why does the hour hand "
                "go around twice in one day, but the minute hand only goes around "
                "once in one hour? Moreover, the numbers on a clock only give "
                "you a rough idea of where the sun is.")
    st.markdown("The **solar clock** fixes these issues by interpolating diurnal "
                "time onto a circle, where 6 AM is always sunrise and 6 PM is "
                "always sunset. Midnight is truly midnight and Noon is truly midday.")
    st.markdown("In solar time, the length of a second varies throughout the course "
                "of a day and over the course of the year. In the summer, solar seconds "
                "are longer than clock seconds during the day, etc.")
    st.info("The clock updates every 10 seconds.")


# --- Math Calculations Execution ---
set_time = dt.datetime.now()
display_time = get_local_time_from_coords(user_lat, user_lon)
sol_time = get_solar_time(user_lat, user_lon, set_time)
figure = show_solar_time(user_lat, user_lon, sol_time, display_time)

# Inject the generated figure back up into the top slot of Column 2
plot_slot.plotly_chart(figure)

# Main Native Script Loop
time.sleep(10)
st.rerun()
