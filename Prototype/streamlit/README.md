
# ParkPulse 1.5 Web Application

## Overview

ParkPulse 1.5 is a web application built with Streamlit, designed to provide users with real-time parking and traffic data, weather predictions, and multimedia content related to parking spaces. This application integrates functionalities such as displaying maps with traffic and parking data, predicting weather conditions, and showing satellite images and videos.

## Files and External Resources

### Python Package Imports:
- `streamlit` (`st`): Framework for building web apps in Python.
- `pandas` (`pd`): Library for data manipulation and analysis.
- `folium`: Library to create interactive maps.
- `streamlit.components.v1` (`components`): For integrating web components with Streamlit apps.
- `joblib`: For saving and loading Python objects efficiently.
- `datetime`: For manipulating dates and times.
- `os`: For interacting with the operating system.

### Model and Data Files:
- `weather_predictor_model.joblib`: Pre-trained machine learning model for weather prediction.
- `Infraestructures_Inventari_Reserves.csv`: CSV file containing parking data.
- `2024_traffic.csv`: CSV file containing traffic data for the year 2024.

### HTML and CSS Code:
- Inside `display_traffic_map` function, `legend_html` contains HTML and CSS for the traffic map legend.

### Local File Paths for Images and Videos:
- Satellite image path: `/path/to/parking.png`
- Video file path: `/path/to/output.mp4`

### Static Assets:
- Satellite image (`parking.png`) and video file (`output.mp4`) are required static assets.

## How to Run

To run ParkPulse 1.5, follow these steps:

1. Ensure you have Python installed on your system.
2. Install the required Python packages using pip:
   ```
   pip install streamlit pandas folium joblib
   ```
3. Place your model, data files, and static assets in the appropriate directory.
4. Navigate to the directory containing the application script.
5. Run the application with Streamlit:
   ```
   streamlit run app_stream.py
   ```
   

After running the command, Streamlit will start the application and provide a local URL to access it through a web browser.

## Note

Ensure all the paths to files and assets within the script are correctly set according to your local setup.
