# ParkPulse Flask Application - README

## Introduction

Welcome to ParkPulse, an innovative parking spot application designed to help users find and reserve parking spots in different neighborhoods. This application features both free and premium functionalities, providing real-time video links and booking options for premium users. It also includes a weather prediction feature, displaying temperature, cloud cover, and humidity information.

## Table of Contents

- [Setup Instructions](#setup-instructions)
- [Environment Variables](#environment-variables)
- [File Descriptions](#file-descriptions)
- [Application Structure](#application-structure)
- [Endpoints](#endpoints)
- [Key Features](#key-features)

## Setup Instructions

### Prerequisites

- Python 3.7 or above
- Flask
- Pandas
- Joblib
- Folium
- Twilio
- Dotenv

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/parkpulse.git
   cd parkpulse
Create and activate a virtual environment:

python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
Install the required packages:


pip install -r requirements.txt
Set environment variables:

Create a .env file in the project root directory and add the following:

TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number

Run the application:

python app.py

Open your browser and navigate to:

http://127.0.0.1:5000

Environment Variables

TWILIO_ACCOUNT_SID: Your Twilio Account SID.

TWILIO_AUTH_TOKEN: Your Twilio Auth Token.

TWILIO_PHONE_NUMBER: Your Twilio Phone Number.

File Descriptions

app.py: The main Flask application file that includes all the routes and logic.

cred.env: Contains environment variables for Twilio credentials.

requirements.txt: Lists all the dependencies required to run the application.

checkpoint5_neighbourhood_district_data.csv: The dataset containing parking spot information.

model.pkl, scaler.pkl, preprocessor.pkl, weather_prediction_model.pkl: Pre-trained models and scalers used in the application.

test.py: A script to generate real-time video using YOLO model.

## Application Structure

app.py

Imports: Imports necessary libraries and modules.

Load Environment Variables: Loads Twilio credentials from cred.env.

Load Data and Models: Loads the dataset and pre-trained models.

Define Weights: Defines weights for calculating the weighted occupancy rate.

Calculate Additional Features: Calculates the is_weekend feature and scales other features.

Routes: Defines various routes for the application.

## Key Functions

index(): Renders the home page and provides a list of districts.

get_neighbourhoods(district): Returns the list of neighborhoods for a given district.

get_weather_data_route(): Provides weather data.

show_map(): Displays the map with parking spots for free users.

show_premium_map(): Displays the map with additional premium features.

video(): Runs a script to generate a real-time video and serves the video file.

book(): Handles booking requests and sends a confirmation SMS.

send_booking_sms(phone_number, address, spot_id): Sends a booking confirmation SMS using Twilio.

get_weather_data(): Generates weather predictions using the pre-trained weather model.

create_map(spots, premium=False): Creates a Folium map with parking spot markers. Adds premium features if premium is True.

## Endpoints

Home Page

URL: /

Method: GET

Description: Displays the home page with a list of districts.

Get Neighborhoods

URL: /get_neighbourhoods/<district>

Method: GET

Description: Returns the list of neighborhoods for the selected district.

Get Weather Data

URL: /get_weather_data

Method: POST

Description: Returns the weather data.

Show Map

URL: /show_map

Method: POST

Description: Displays the map with parking spots for free users.

Show Premium Map

URL: /show_premium_map

Method: POST

Description: Displays the map with additional premium features like real-time video links and booking options.

Video

URL: /video

Method: GET

Description: Generates a real-time video for the selected parking spot and serves the video file.

Book

URL: /book

Method: POST

Description: Handles booking requests and sends a confirmation SMS.

## Key Features

Free Features

Interactive Map: Displays parking spots in the selected neighborhood.

Weather Information: Shows temperature, cloud cover, and humidity on the page.

## Premium Features

Real-Time Video Links: Provides a link to watch a live video of the parking spot.

Booking: Allows users to book a parking spot and receive a confirmation SMS.
