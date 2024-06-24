#### - file "weather.ipynb":  
3 weather predictive models for temperature, humidity and cloud cover.  
For the temperature it's ok (accuracy 99%), for the others not.  
So the next step is to improve the 2 models to predict humidity and cloud cover.
      
#### - file "weather&traffic.ipynb":  
It's an analysis to show that the weather and the data traffic are not correlated so that we decide to use only the weather data to predict the weather and separately only the traffic data to predict the traffic.  
As in 1), here the traffic data are from tom-tom (not really useful), so the next step is to replace them with the new traffic data (from 2021 to 2024).    
After having replaced the old traffic data with the new ones, to predict the weather we continue to use only the weather data (because they don't depend on the traffic), instead to predict the traffic we will use both the traffic and the weather data (because the traffic depends also on the weather, for example if it rains). 
