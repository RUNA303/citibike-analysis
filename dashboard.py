import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime as dt
# --- NEW IMPORTS ---
import json
from keplergl import KeplerGl
from streamlit_keplergl import keplergl_static
# --- END NEW IMPORTS ---

# --- Page Configuration (Set this first!) ---
st.set_page_config(
    page_title="JC Bike Share Dashboard",
    page_icon="🚲",
    layout="wide"
)

# --- Title and Description ---
st.title("Jersey City / Hoboken Bike Share Data Dashboard")
st.write("""
This dashboard visualizes bike share usage patterns based on the provided dataset.
It shows the most popular starting stations and the relationship between daily rides and temperature.
Data appears to be from Jersey City/Hoboken based on station names.
""")

# --- Load Data ---
file_path = '/Users/runi/Downloads/processed_data.csv' # Adjust if needed

@st.cache_data
def load_data(path):
    try:
        df = pd.read_csv(path, index_col=0)
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        df['value'] = 1
        # Ensure lat/lon columns are numeric if they aren't already
        for col in ['start_lat', 'start_lng', 'end_lat', 'end_lng']:
             if col in df.columns:
                 df[col] = pd.to_numeric(df[col], errors='coerce')
        df.dropna(subset=['start_lat', 'start_lng'], inplace=True) # Drop rows where essential geo-data is missing
        return df
    except FileNotFoundError:
        st.error(f"Error: Data file not found at {path}. Please ensure the file exists.")
        return None
    except Exception as e:
        st.error(f"An error occurred while loading the data: {e}")
        return None

df = load_data(file_path)

# --- Proceed only if data is loaded ---
if df is not None:

    st.header("Most Popular Start Stations")
    # ... (Bar Chart Code as before - no changes needed here) ...
    # --- Bar Chart Data Wrangling ---
    df_groupby_bar = df.groupby('start_station_name', as_index=False).agg({'value': 'sum'})
    top20 = df_groupby_bar.nlargest(20, 'value')

    # --- Create Bar Chart ---
    if not top20.empty:
        fig_bar = px.bar(
            top20, x='start_station_name', y='value',
            labels={'start_station_name': 'Start Station', 'value': 'Number of Trips'},
            color='value', color_continuous_scale='Blues'
        )
        fig_bar.update_layout(xaxis_tickangle=-45, xaxis_title='Start Station', yaxis_title='Number of Trips', title_x=0.5)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("No data available for the top stations bar chart.")


    st.header("Daily Rides vs. Temperature")
    # ... (Line Chart Code as before - no changes needed here) ...
     # --- Line Chart Data Wrangling ---
    daily_rides = df.groupby('date').agg(bike_rides_daily=('value', 'sum')).reset_index()
    daily_temp = df[['date', 'avgTemp']].drop_duplicates().sort_values('date').reset_index(drop=True)
    df_line = pd.merge(daily_rides, daily_temp, on='date', how='left')

    # --- Create Dual-Axis Line Chart ---
    if not df_line.empty:
        fig_line = make_subplots(specs=[[{"secondary_y": True}]])
        fig_line.add_trace(go.Scatter(x=df_line['date'], y=df_line['bike_rides_daily'], name='Daily Bike Rides'), secondary_y=False,)
        fig_line.add_trace(go.Scatter(x=df_line['date'], y=df_line['avgTemp'], name='Avg Daily Temperature'), secondary_y=True,)
        fig_line.update_xaxes(title_text='Date')
        fig_line.update_yaxes(title_text='Number of Bike Rides', secondary_y=False)
        fig_line.update_yaxes(title_text='Average Temperature', secondary_y=True)
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.warning("No data available for the daily rides vs temperature line chart.")


    # --- Kepler.gl Map using JSON Config (Modified Section) ---
    st.header("Kepler.gl Map Visualization")

    # --- IMPORTANT: Assumes 'kepler_config.json' is in the same directory ---
    map_file_path = 'nyc_bike_trips_map.html'
    config_file_path = 'nyc_bike_trips_map_config.json'

    try:
        # 1. Load the JSON configuration file
        with open(config_file_path, 'r') as f:
            kepler_config = json.load(f)
        st.write(f"Loaded Kepler configuration from: `{config_file_path}`") # Optional: confirm loading
        with open(map_file_path, 'r', encoding='utf-8') as f:
            html_map = f.read()
        st.components.v1.html(html_map, height=900) # Adjust height as needed
        st.caption("Note: This map requires the 'kepler_bike_map.html' file generated separately.")
    except FileNotFoundError:
        st.error(f"Error: Kepler map file not found at '{map_file_path}'. Please generate it and place it in the correct directory.")
    except Exception as e:
        st.error(f"An error occurred displaying the Kepler map: {e}")

else:
    st.error("Dashboard cannot be displayed because the data failed to load.")



        
        # 2. Create a KeplerGl map object
        #    You might need to adjust the initial height
        #    You can optionally pass the loaded config directly here:
        #    map_object = KeplerGl(height=600, config=kepler_config)
        #    Or load it after adding data (shown below)
#        map_object = KeplerGl(height=900) # Adjust height as needed

        # 3. Add your DataFrame to the map object.
        #    Give the dataset a name (e.g., 'bike_data') that might be
        #    referenced within your JSON config. Check your config file.
        #    Make sure the DataFrame 'df' contains the necessary columns
        #    (like start_lat, start_lng) that your config expects.
 #       map_object.add_data(data=df, name='bike_data') # Use a relevant name

        # 4. Assign the loaded configuration to the map object's config
        #    (Alternative to passing it during creation)
  #      map_object.config = kepler_config

        # 5. Display the map object using keplergl_static
#        keplergl_static(map_object, center_map=False) # center_map=False might respect the initial view in your config better
 #       st.caption("Note: This map uses data loaded in the app and configuration from 'kepler_config.json'.")

  #  except FileNotFoundError:
   #     st.error(f"Error: Kepler configuration file not found at '{config_file_path}'. Please ensure the file exists.")
 #   except json.JSONDecodeError:
   #      st.error(f"Error: Could not decode '{config_file_path}'. Please ensure it is a valid JSON file.")
  #  except Exception as e:
    #    st.error(f"An error occurred displaying the Kepler map: {e}")
     #   st.error("Check if the dataset name in add_data() matches references in your JSON config.")

#else:
 #   st.error("Dashboard cannot be displayed because the data failed to load.")


