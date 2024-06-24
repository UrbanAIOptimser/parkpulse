#### - file "weather_parking_traffic.ipynb":  
It's the merging of parking, weather and traffic (tom-tom so only from december 2019 to november 2020) + parking predictive model (with accuracy 90%).  
So the next step here is to replace the tom-tom with the new traffic data (from 2021 to 2024) and repeat the parking model with these new data.


#### - file "LAST_MERGING_MODEL.ipynb":  
New merging using the new traffic and parking data (year 2024). So combining the data of parking, weather and traffic, we predict the number of parking spots available.
Merging dataset "df_traffic_parking_weather_weather.csv" in the folder "data".

 
#### - file "prob_model.ipynb":
Analyze and predict urban parking occupancy using statistical models and machine learning algorithms.   
We will use a dataset containing meteorological and parking occupancy data in various neighborhoods of Barcelona. Our approach involves the use of preprocessing techniques to prepare the data, followed by building a predictive model based on Random Forest. Furthermore, we will calculate future employment probabilities and analyze time-dependent model properties.


