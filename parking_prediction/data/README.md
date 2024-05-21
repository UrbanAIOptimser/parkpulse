# Explanation to join the parking, weather and traffic data:
#### (So the file "df_traffic_parking_weather_weather.csv")
Merging Weather and Traffic:
    # Step 1: Find all the unique combinations of dates between the two dataframes
    # Step 2: Loop through each unique date
    # Step 3: Calculate the distance between coordinates using haversine
    # Step 4: Join by the nearest neighbourhood.


————————haversine———————————————————
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = 6371 * c  # Earth radius in kilometers
    return distance



——————————join by nearest neighbourhood——————————————————————
def create_join_by_date_distance_coordinate(df_weather, df_traffic):
    results = []
    
    
    unique_dates = set(df_weather['date']).intersection(set(df_traffic['date']))
    
    
    for date in unique_dates:
        weather_subset = df_weather[df_weather['date'] == date]
        traffic_subset = df_traffic[df_traffic['date'] == date]
        if weather_subset.empty or traffic_subset.empty:
            continue
        
        
    
        for index_A, row_A in weather_subset.iterrows():
            distances = [haversine(row_A['latitude'], row_A['longitude'], row_B['Latitud'], \
                                   row_B['Longitud']) for index_B, row_B in traffic_subset.iterrows()]
            nearest_index = distances.index(min(distances))
            merged_row = {**row_A, **traffic_subset.iloc[nearest_index]}
            results.append(merged_row)
    return results


Merging Weather and Traffic with Parking:
	# Step 1: Calculate midpoints of parking segments
	# Step 2: Loop through the Parking data and the weather_traffic data 
	# Step 3: Calculate the distance between coordinates using haversine
 	# Step 4: Join by the nearest neighbourhood.

————————————————Midpoint—————————————————————————
def midpoint(lat1, lon1, lat2, lon2):
    return (lat1 + lat2) / 2, (lon1 + lon2) / 2

————————————Join by the nearest neighbour———————————————————
def find_nearest_weather(df_parking, weather_df):
    results = []
    for index_A, row_A in weather_df.iterrows():
        distances = [haversine(row_A['latitude'], row_A['longitude'], row_B['mid_latitude'], \
                               row_B['mid_longitude']) for index_B, row_B in df_parking.iterrows()]
        nearest_index = distances.index(min(distances))
        merged_row = {**row_A, **df_parking.iloc[nearest_index]}
        results.append(merged_row)
    return results
