# In github in the folder "parking_prediction" we have:

### 1) "weather_parking_traffic.ipynb":  
It's the merging of parking, weather and traffic (tom-tom so only from december 2019 to november 2020) + parking predictive model (with accuracy 90%).  
So the next step here is to replace the tom-tom with the new traffic data (from 2021 to 2024) and repeat the parking model with these new data.

### 2) "2024_traffic.ipynb":  
It's an analysis of the traffic in the first 3 months of the year 2024 + traffic prediction model (it's classification because the current traffic status is categorical) with an accuracy of 79%.  
So the next step is to improve the performance of the model (also find a way to merge all the traffic data from 2021 to 2024).  
At the moment, at the end of this file there is the merging of the 2024 traffic with the parking data, but the paking data we have now are until 2023, so now we can't merge them.

### 3) folder "weather" with the files:  
#### -- "weather.ipynb":  
3 weather predictive models for temperature, humidity and cloud cover.  
For the temperature it's ok (accuracy 99%), for the others not.  
So the next step is to improve the 2 models to predict humidity and cloud cover.
      
#### -- "weather&traffic.ipynb":  
It's an analysis to show that the weather and the data traffic are not correlated so that we decide to use only the weather data to predict the weather and separately only the traffic data to predict the traffic.  
As in 1), here the traffic data are from tom-tom (not really useful), so the next step is to replace them with the new traffic data (from 2021 to 2024).    
After having replaced the old traffic data with the new ones, to predict the weather we continue to use only the weather data (because they don't depend on the traffic), instead to predict the traffic we will use both the traffic and the weather data (because the traffic depends also on the weather, for example if it rains).  

### 4) folder "traffic" now empty.
