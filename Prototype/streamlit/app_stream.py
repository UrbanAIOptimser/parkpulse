import streamlit as st
import pandas as pd
import folium
import streamlit.components.v1 as components
import joblib
from datetime import datetime
import os

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
    filtered_data = parking_data[
        (parking_data['Nom_Districte'] == district_name) & 
        (parking_data['Nom_Barri'] == neighborhood_name)
    ]
    
    barcelona_map = folium.Map(location=[41.3851, 2.1734], zoom_start=13)

    for _, row in filtered_data.iterrows():
        popup_html = f"""
            <b>ID Reserva:</b> {row['ID_Reserva']}<br>
            <b>Location:</b> {row['Nom_Barri']}<br>
            <a href='#' target='_blank'>View Satellite Image</a><br>
            <a href='#' target='_blank'>View Video</a>
        """
        folium.Marker(
            location=[row['Latitud'], row['Longitud']],
            popup=folium.Popup(popup_html, max_width=450),
            tooltip=row['Codi_Reserva']
        ).add_to(barcelona_map)

    map_html = barcelona_map._repr_html_()
    components.html(map_html, height=500)

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

# Function to display a specific satellite image
def display_satellite_image():
    # Specify the path to your image file
    image_path = "/Users/joaquintejo/Desktop/BTS/FINAL_PROJECT/CHECKPOINT3/ParkPulse_Dashboard/DinamicMap/static/parking/parking.png"
    if os.path.exists(image_path):
        st.image(image_path, caption="Satellite Image")
    else:
        st.error("Satellite image not found.")

# Function to display a video
def display_video():
    # Specify the path to your video file
    video_path = "/Users/joaquintejo/Desktop/BTS/FINAL_PROJECT/CHECKPOINT3/ParkPulse_Dashboard/DinamicMap/static/output.mp4"
    if os.path.exists(video_path):
        st.video(video_path)
    else:
        st.error("Video not found.")

def main():
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
        
    if st.button("Show Satellite Image"):
        display_satellite_image()
    
    if st.button("Show Video"):
        display_video()

if __name__ == '__main__':
    main()

