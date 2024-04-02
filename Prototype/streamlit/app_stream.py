import streamlit as st
import pandas as pd
import subprocess
import folium
import streamlit.components.v1 as components
from streamlit_folium import folium_static
import joblib
from datetime import datetime
import os
import cv2
import pickle
from PIL import Image
import numpy as np

# Load the weather prediction model
model_path = 'weather_predictor_model.joblib'
model = joblib.load(model_path)

# Load parking data
parking_data_path = "Infraestructures_Inventari_Reserves.csv"
parking_data = pd.read_csv(parking_data_path)

def display_traffic_map():
    # Load traffic data
    df_traffic_2024 = pd.read_csv('2024_traffic.csv')
    
    # Generate the traffic map
    agg_data = df_traffic_2024.groupby('idTram').agg({
        'Longitud': 'mean',
        'Latitud': 'mean',
        'estatActual': 'last',
        'Descripció': 'first'
    }).reset_index()

    map_center = [agg_data['Latitud'].mean(), agg_data['Longitud'].mean()]
    traffic_map = folium.Map(location=map_center, tiles='cartodbpositron', zoom_start=13)

    colors = {
        0: 'gray',
        1: 'green',
        2: 'lightgreen',
        3: 'yellow',
        4: 'orange',
        5: 'red',
        6: 'black'
    }

    for _, row in agg_data.iterrows():
        folium.CircleMarker(
            location=[row['Latitud'], row['Longitud']],
            radius=5,
            color=colors[row['estatActual']],
            fill=True,
            fill_color=colors[row['estatActual']],
            fill_opacity=0.7,
            popup=folium.Popup(f"{row['Descripció']}: Status {row['estatActual']}", parse_html=True)
        ).add_to(traffic_map)

    # Add the legend HTML
    legend_html = '''
    <div style="position: fixed; 
         bottom: 50px; left: 50px; width: 150px; height: 125px; 
         border:2px solid grey; z-index:9999; font-size:14px;
         background:white;
         ">&nbsp; <b>Traffic Status</b> <br>
         &nbsp; Very Fluid &nbsp; <i style="background:green;width:10px;height:10px;display:inline-block;"></i><br>
         &nbsp; Fluid &nbsp; <i style="background:lightgreen;width:10px;height:10px;display:inline-block;"></i><br>
         &nbsp; Dense &nbsp; <i style="background:yellow;width:10px;height:10px;display:inline-block;"></i><br>
         &nbsp; Very Dense &nbsp; <i style="background:orange;width:10px;height:10px;display:inline-block;"></i><br>
         &nbsp; Congested &nbsp; <i style="background:red;width:10px;height:10px;display:inline-block;"></i><br>
         &nbsp; Closed &nbsp; <i style="background:black;width:10px;height:10px;display:inline-block;"></i>
    </div>
    '''
    traffic_map.get_root().html.add_child(folium.Element(legend_html))

    # Convert map to HTML string and display
    map_html = traffic_map._repr_html_()
    components.html(map_html, height=500)

def display_parking_map(district_name, neighborhood_name):
    # Filter data for the selected district and neighborhood
    filtered_data = parking_data[
        (parking_data['Nom_Districte'] == district_name) &
        (parking_data['Nom_Barri'] == neighborhood_name)
    ]
    
    # Create the folium map
    m = folium.Map(location=[41.3851, 2.1734], zoom_start=13)
    for _, row in filtered_data.iterrows():
        folium.Marker(
            location=[row['Latitud'], row['Longitud']],
            popup=f"ID Reserva: {row['ID_Reserva']}<br>Location: {row['Nom_Barri']}",
            tooltip=row['Codi_Reserva']
        ).add_to(m)
    
    # Display the map in the Streamlit app
    folium_static(m)

def create_clickable_map(filtered_data):
    # Create a folium map instance
    m = folium.Map(location=[41.3851, 2.1734], zoom_start=13)

    # Use the same image and video for all pins
    image_path = "static/parking/parking.png"
    video_path = "static/output.mp4"

    # Iterate over the rows of the dataframe and create a marker for each parking spot
    for _, row in filtered_data.iterrows():
        popup_html = f"""
            <b>ID Reserva:</b> {row['ID_Reserva']}<br>
            <b>Location:</b> {row['Nom_Barri']}<br>
            <a href="#" onclick="window.open('{image_path}'); return false;">View Satellite Image</a><br>
            <a href="#" onclick="window.open('{video_path}'); return false;">View Video</a>
        """
        folium.Marker(
            location=[row['Latitud'], row['Longitud']],
            popup=folium.Popup(popup_html, max_width=450),
            tooltip=row['Codi_Reserva']
        ).add_to(m)

    # Display the map in the Streamlit app
    folium_static(m)

def predict_weather():
    features = [20, 10, 19, 11, 5, 70, 0.5, 0.2, 0, 0, 25, 10, 150, 1015, 50, 10, 200, 5, 5, 1000]
    predicted_temp = model.predict([features])[0]
    today = datetime.today()
    humidity = 70
    cloudcover = 50

    return {
        'date': today.strftime("%Y-%m-%d"),
        'predicted_temperature': predicted_temp,
        'humidity': humidity,
        'cloudcover': cloudcover
    }

def display_satellite_image(id_reserva):
    image_path = "/Users/joaquintejo/Desktop/BTS/FINAL_PROJECT/CHECKPOINT3/ParkPulse_Dashboard/DinamicMap/static/parking/parking.png"
    if os.path.exists(image_path):
        st.image(image_path, caption="Satellite Image")
    else:
        st.error("Satellite image not found.")

def display_video(id_reserva):
    try:
        result = subprocess.run(['python', 'test.py'], capture_output=True, text=True, check=True)
        video_path = "/Users/joaquintejo/Desktop/BTS/FINAL_PROJECT/CHECKPOINT3/ParkPulse_Dashboard/DinamicMap/static/output.mp4"
        if os.path.exists(video_path):
            st.video(video_path)
        else:
            st.error("Video not found.")
    except subprocess.CalledProcessError as e:
        st.error(f"Error generating video: {e}")

def main():
    # Conditionally render sidebar buttons based on the current view
    if 'view' not in st.session_state or st.session_state['view'] == 'main':
        if st.sidebar.button("Go to Developers Section"):
            st.session_state['view'] = 'developers'
            st.experimental_rerun()
    elif st.session_state['view'] == 'developers':
        if st.sidebar.button("Back to Main App"):
            st.session_state['view'] = 'main'
            st.experimental_rerun()

    # Use session state to toggle between views
    if st.session_state.get('view') == 'developers':
        developers_view()
    else:
        parkpulse_view()

    # Event handling for displaying images and videos moved to parkpulse_view

def parkpulse_view():
    st.title("ParkPulse 1.5")

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.write(f"Current Time: {current_time}")

    districts = parking_data['Nom_Districte'].dropna().unique().tolist()
    district = st.selectbox("Select your district:", [""] + districts)

    neighborhood = ""
    if district:
        neighborhoods = parking_data[parking_data['Nom_Districte'] == district]['Nom_Barri'].unique().tolist()
        neighborhood = st.selectbox("Select your neighborhood:", [""] + neighborhoods)

    if st.button("Find Parking Spot") and district and neighborhood:
        display_parking_map(district, neighborhood)

    if st.button("View Traffic Status"):
        display_traffic_map()

    if st.button("How is the Weather Today?"):
        weather_info = predict_weather()
        st.write("🌡️ Predicted temperature for today is:", weather_info['predicted_temperature'], "°C")
        st.write("💧 Humidity:", weather_info['humidity'], "%")
        st.write("☁️ Cloud Cover:", weather_info['cloudcover'], "%")

def developers_view():
    st.title('Parking Space Picker')

    width, height = 40, 23

    try:
        with open('park_positions.pkl', 'rb') as f:
            park_positions = pickle.load(f)
    except FileNotFoundError:
        park_positions = []
        with open('park_positions.pkl', 'wb') as f:
            pickle.dump(park_positions, f)

    img_path = '/Users/joaquintejo/Desktop/BTS/FINAL_PROJECT/CHECKPOINT3/ParkPulse_Dashboard/Parking_space_counter/input/parking.png'
    if os.path.exists(img_path):
        img = cv2.imread(img_path)
        for position in park_positions:
            top_left = (position[0], position[1])
            bottom_right = (position[0] + width, position[1] + height)
            cv2.rectangle(img, top_left, bottom_right, (255, 0, 255), 3)
        st.image(img, use_column_width=True)
    else:
        st.error("Parking lot image not found.")

    with st.form(key='parking_space_form'):
        st.write("Add a parking space")
        x = st.number_input('Enter X coordinate', min_value=0, max_value=1000) # Adjust max_value according to your image dimensions
        y = st.number_input('Enter Y coordinate', min_value=0, max_value=1000) # Adjust max_value accordingly
        submit_button = st.form_submit_button(label='Add Parking Space')
        if submit_button:
            park_positions.append((int(x), int(y)))
            with open('park_positions.pkl', 'wb') as f:
                pickle.dump(park_positions, f)
            st.experimental_rerun()

    remove_slot = st.selectbox('Remove a parking space', [''] + [f'{p[0]}, {p[1]}' for p in park_positions])
    if st.button('Remove Selected Parking Space') and remove_slot:
        park_positions.remove(tuple(map(int, remove_slot.split(', '))))
        with open('park_positions.pkl', 'wb') as f:
            pickle.dump(park_positions, f)
        st.experimental_rerun()

if __name__ == '__main__':
    main()

