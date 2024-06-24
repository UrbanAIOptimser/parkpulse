import os
import subprocess
from flask import Flask, render_template, request, jsonify, send_from_directory
import pandas as pd
import joblib
import folium
from folium.plugins import MarkerCluster
from datetime import datetime
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('cred.env')

app = Flask(__name__)

# Load the data and models
data_path = 'checkpoint5_neighbourhood_district_data.csv'
model_path = 'models/model.pkl'
scaler_path = 'models/scaler.pkl'
preprocessor_path = 'models/preprocessor.pkl'
weather_model_path = 'models/weather_prediction_model.pkl'
weather_model_features_path = 'models/weather_prediction_model_with_features.pkl'

data = pd.read_csv(data_path)
model = joblib.load(model_path)
scaler = joblib.load(scaler_path)
preprocessor = joblib.load(preprocessor_path)
weather_model = joblib.load(weather_model_path)

# Twilio configuration using environment variables
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Define weights for weighted average
weights = {
    'estimated_occupancy_rate': 0.5, 
    'precipitation': 0.15, 
    'visibility': 0.1, 
    'cloud_cover': 0.1, 
    'is_weekend': 0.1, 
    'snow': 0.1, 
    'temp': 0.1
}

# Calculate additional features
data['is_weekend'] = pd.to_datetime(data['datetime']).dt.weekday >= 5
data[['precipitation', 'visibility', 'cloud_cover', 'snow', 'temp']] = scaler.transform(data[['precipitation', 'visibility', 'cloud_cover', 'snow', 'temp']])
data['weighted_occupancy'] = (
    data['estimated_occupancy_rate'] * weights['estimated_occupancy_rate'] +
    data['precipitation'] * weights['precipitation'] +
    data['visibility'] * weights['visibility'] +
    data['cloud_cover'] * weights['cloud_cover'] +
    data['is_weekend'] * weights['is_weekend'] +
    data['snow'] * weights['snow'] +
    data['temp'] * weights['temp']
)

@app.route('/')
def index():
    districts = data['district'].unique()
    return render_template('index.html', districts=districts)

@app.route('/get_neighbourhoods/<district>')
def get_neighbourhoods(district):
    neighbourhoods = data[data['district'] == district]['neighbourhood_bcn'].unique()
    return jsonify(neighbourhoods.tolist())

@app.route('/get_weather_data', methods=['POST'])
def get_weather_data_route():
    weather_data = get_weather_data()
    return jsonify(weather_data)

@app.route('/show_map', methods=['POST'])
def show_map():
    district = request.form.get('district')
    neighbourhood = request.form.get('neighbourhood')
    
    spots = data[(data['district'] == district) & (data['neighbourhood_bcn'] == neighbourhood)]
    
    # Debugging: Print the number of spots found
    print(f"Selected district: {district}")
    print(f"Selected neighbourhood: {neighbourhood}")
    print(f"Number of spots found: {len(spots)}")
    print(spots[['district', 'neighbourhood_bcn', 'latitude_start', 'longitude_start', 'address.1', 'places', 'type', 'schedule_description', 'tariff_description']])
    
    map_html = create_map(spots)
    return map_html

@app.route('/show_premium_map', methods=['POST'])
def show_premium_map():
    district = request.form.get('district')
    neighbourhood = request.form.get('neighbourhood')
    
    spots = data[(data['district'] == district) & (data['neighbourhood_bcn'] == neighbourhood)]
    
    # Debugging: Print the number of spots found
    print(f"Selected district: {district}")
    print(f"Selected neighbourhood: {neighbourhood}")
    print(f"Number of spots found: {len(spots)}")
    print(spots[['district', 'neighbourhood_bcn', 'latitude_start', 'longitude_start', 'address.1', 'places', 'type', 'schedule_description', 'tariff_description']])
    
    map_html = create_map(spots, premium=True)
    return map_html

@app.route('/video')
def video():
    try:
        result = subprocess.run(['python', 'test.py'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return "Server Error: Unable to generate video", 500
    except Exception as e:
        print(f"Exception: {str(e)}")
        return "Server Error: Unable to run video script", 500

    VIDEO_DIR = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(VIDEO_DIR, 'output.mp4')

@app.route('/book', methods=['POST'])
def book():
    phone_number = request.form.get('phone_number')
    address = request.form.get('address')
    spot_id = request.form.get('spot_id')
    
    # Send booking confirmation SMS
    send_booking_sms(phone_number, address, spot_id)
    return jsonify({'status': 'success', 'message': 'Booking confirmed. A confirmation SMS has been sent.'})

def send_booking_sms(phone_number, address, spot_id):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    message = client.messages.create(
        body=f"Your booking for the parking spot at {address} (ID: {spot_id}) has been confirmed. Your ParkPulse Team.",
        from_=TWILIO_PHONE_NUMBER,
        to=phone_number
    )
    print(f"Sent SMS to {phone_number}: {message.sid}")

def get_weather_data():
    # Define features as used during training
    features = {
        'tempmax': 20.0,
        'tempmin': 10.0,
        'feelslikemax': 18.0,
        'feelslikemin': 8.0,
        'dew': 12.0,
        'precip': 0.0,
        'windgust': 30.0,
        'windspeed': 15.0,
        'winddir': 180.0,
        'pressure': 1015.0,
        'visibility': 10.0,
        'solarradiation': 200.0,
        'solarenergy': 5.0,
        'uvindex': 5,
        'month': datetime.now().month,
        'day': datetime.now().day,
        'hour': datetime.now().hour
    }
    features_df = pd.DataFrame([features])

    # Ensure the feature names match those used during model training
    required_features_weather = weather_model.feature_names_in_
    features_df = features_df[required_features_weather]

    prediction = weather_model.predict(features_df)[0]
    temp, humidity, cloud_cover = round(prediction[0], 2), round(prediction[1], 2), round(prediction[2], 2)
    return {'temp': temp, 'humidity': humidity, 'cloud_cover': cloud_cover}

def create_map(spots, premium=False):
    if spots.empty:
        return "No parking spots found for the selected neighborhood."
    
    m = folium.Map(location=[spots['latitude_start'].mean(), spots['longitude_start'].mean()], zoom_start=15)
    marker_cluster = MarkerCluster().add_to(m)
    
    for _, spot in spots.iterrows():
        # Prepare input data for prediction
        input_data = pd.DataFrame({
            'icon': [spot['icon']],
            'moon_phase': [spot['moon_phase']],
            'neighbourhood_bcn': [spot['neighbourhood_bcn']],
            'weighted_occupancy': [spot['weighted_occupancy']]
        })
        probability = model.predict(input_data)[0]
        
        # Prepare the popup content with all the information
        popup_content = (
            f"<div style='width: 300px;'>"
            f"<b>Address:</b> {spot['address.1']}<br>"
            f"<b>Places:</b> {spot['places']}<br>"
            f"<b>Type:</b> {spot['type']}<br>"
            f"<b>Schedule:</b> {spot['schedule_description']}<br>"
            f"<b>Tariff:</b> {spot['tariff_description']}<br>"
            f"<b>Probability of finding a spot:</b> {probability:.2f}%"
        )

        if premium:
            # Add premium information (real-time video link, booking button)
            video_link = f"<a href='/video?spot_id={spot['id_tram']}' target='_blank'>Watch Live Video</a>"
            booking_form = (
                f"<form method='post' action='/book' class='mt-2'>"
                f"<input type='hidden' name='spot_id' value='{spot['id_tram']}'>"
                f"<input type='hidden' name='address' value='{spot['address.1']}'>"
                f"<div class='form-group'>"
                f"<label for='phone_number'>Phone Number:</label>"
                f"<input type='text' class='form-control' name='phone_number' required>"
                f"</div>"
                f"<button type='submit' class='btn btn-success btn-block'>Book Now</button>"
                f"</form>"
            )
            popup_content += f"<br>{video_link}<br>{booking_form}"
        
        popup_content += "</div>"
        
        folium.Marker(
            location=[spot['latitude_start'], spot['longitude_start']],
            popup=folium.Popup(popup_content, max_width=300),
            icon=folium.Icon(color='blue')
        ).add_to(marker_cluster)
    
    return m._repr_html_()

if __name__ == '__main__':
    app.run(debug=True)




































    