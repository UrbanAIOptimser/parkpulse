#!/usr/bin/env python
# coding: utf-8

# # Data Preparation and Cleaning

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler, normalize, MinMaxScaler
import scipy.cluster.hierarchy as shc
from sklearn.cluster import AgglomerativeClustering
import numpy as np
from sklearn.metrics import silhouette_score
from geopy.geocoders import Nominatim
from time import sleep

geolocator = Nominatim(user_agent="my_geocoder")


def get_location_info(row):
    latitude, longitude = row["mid_latitude"], row["mid_longitude"]
    # print(latitude, longitude)
    # sleep(2)
    try:
        location = geolocator.reverse((latitude, longitude), exactly_one=True)
        address = location.raw.get("address", {})
        place_rank = location.raw.get("place_rank", "UNKNOWN")
        importance = location.raw.get("importance", "UNKNOWN")
        name = location.raw.get("name", "UNKNOWN")
        district = address.get("suburb", "UNKNOWN")
        neighbourhood = address.get("neighbourhood", "UNKNOWN")
        # neighbourhood = address.get('suburb', address.get('neighbourhood', 'UNKNOWN'))
        quarter = address.get("quarter", "UNKNOWN")
        df = pd.Series([name, neighbourhood, quarter, district, place_rank, importance])
        # print(df)
        return pd.Series(
            [name, neighbourhood, quarter, district, place_rank, importance]
        )
    except Exception as e:
        print(f"Error geocoding {latitude}, {longitude}: {e}")
        return pd.Series(["UNKNOWN"] * 7)


def estimate_occupancy(row):
    # Use traffic, weather, and event data proxies to estimate occupancy
    # This is a simplified example, adjust based on your data
    traffic_factor = row["current_status"] / 100
    weather_factor = 1 if row["conditions"] in ["Rain", "Snow"] else 0.5
    event_factor = 1 if row["event"] else 0.5

    estimated_occupancy = traffic_factor * weather_factor * event_factor * row["places"]
    return estimated_occupancy


df = pd.read_csv("df_traffic_parking_weather_weather.csv")


rename_dict = {
    "Unnamed: 0.1": "unnamed_0_1",
    "Unnamed: 0": "unnamed_0",
    "datetime": "datetime",
    "datetimeEpoch": "datetime_epoch",
    "tempmax": "temp_max",
    "tempmin": "temp_min",
    "temp": "temp",
    "feelslikemax": "feels_like_max",
    "feelslikemin": "feels_like_min",
    "feelslike": "feels_like",
    "dew": "dew_point",
    "humidity": "humidity",
    "precip": "precipitation",
    "precipprob": "precip_probability",
    "precipcover": "precip_coverage",
    "preciptype": "precipitation_type",
    "snow": "snow",
    "snowdepth": "snow_depth",
    "windgust": "wind_gust",
    "windspeed": "wind_speed",
    "winddir": "wind_direction",
    "pressure": "pressure",
    "cloudcover": "cloud_cover",
    "visibility": "visibility",
    "solarradiation": "solar_radiation",
    "solarenergy": "solar_energy",
    "uvindex": "uv_index",
    "sunrise": "sunrise",
    "sunriseEpoch": "sunrise_epoch",
    "sunset": "sunset",
    "sunsetEpoch": "sunset_epoch",
    "moonphase": "moon_phase",
    "conditions": "conditions",
    "description": "description",
    "icon": "icon",
    "stations": "stations",
    "source": "source",
    "latitude": "latitude",
    "longitude": "longitude",
    "resolvedAddress": "resolved_address",
    "address": "address",
    "timezone": "timezone",
    "tzoffset": "timezone_offset",
    "severerisk": "severe_risk",
    "date": "date",
    "ID_TRAM": "id_tram",
    "UTM_IX": "utm_ix",
    "UTM_FX": "utm_fx",
    "UTM_IY": "utm_iy",
    "UTM_FY": "utm_fy",
    "LATITUD_I": "latitude_start",
    "LONGITUD_I": "longitude_start",
    "LATITUD_F": "latitude_end",
    "LONGITUD_F": "longitude_end",
    "ID_TARIFA": "tariff_id",
    "ID_HORARIO": "schedule_id",
    "TIPUS_TRAM": "section_type",
    "ADREÇA": "address",
    "PLACES": "places",
    "pCOLOR": "p_color",
    "RGB": "rgb",
    "COLOR": "color",
    "TYPE": "type",
    "CODI_HORARI": "schedule_code",
    "DESCRIPTION_HORARI": "schedule_description",
    "DESC_CURTA_HORARI": "short_schedule_description",
    "INCLUS_FESTIUS": "include_holidays",
    "PARQUING_SOLS_DINS_HORARI": "parking_within_schedule",
    "ID_TIPUS_TARIFA": "tariff_type_id",
    "CODI_TARIFA": "tariff_code",
    "TIPUS_FRACCIO": "fraction_type",
    "TEMPS_MAXIM": "max_time",
    "TEMPS_MINIM": "min_time",
    "DESCRIPTION_TARIFA": "tariff_description",
    "DESC_CURTA_TARIFA": "short_tariff_description",
    "IMPORT_FRACCIO": "fraction_amount",
    "IMPORT_MAXIM": "max_amount",
    "mid_latitude": "mid_latitude",
    "mid_longitude": "mid_longitude",
    "Descripció": "description",
    "Longitud": "longitude",
    "Latitud": "latitude",
    "estatActual": "current_status",
    "estatPrevist": "predicted_status",
    "Tram_Components": "section_components",
}

df = df.rename(columns=rename_dict)


df.drop(columns=["unnamed_0_1", "unnamed_0_1", "unnamed_0"], axis=0, inplace=True)


df["datetime"] = pd.to_datetime(df["datetime"])
df["day_of_week"] = df["datetime"].dt.day_name()


df[["name", "neighbourhood", "quarter", "district", "place_rank", "importance"]] = (
    df.apply(get_location_info, axis=1)
)

df["month"] = df["datetime"].dt.day
df["day"] = df["datetime"].dt.month
df["year"] = df["datetime"].dt.year


df["is_weekend"] = df["day_of_week"].apply(
    lambda x: 1 if x in ("Saturday", "Sunday") else 0
)

df["neighbourhood"] = df["neighbourhood"].replace("UNKNOWN", np.nan)


df["neighbourhood_bcn"] = df["neighbourhood"].combine_first(df["quarter"])


# ##### Useful Fields for Predicting Parking Availability

# Temporal Fields
#
# 	•	datetime
# 	•	day_of_week
# 	•	date
#
# Weather Data
#
# 	•	temp_max, temp_min, temp
# 	•	feels_like_max, feels_like_min, feels_like
# 	•	dew_point
# 	•	humidity
# 	•	precipitation, precip_probability, precip_coverage, precipitation_type
# 	•	snow, snow_depth
# 	•	wind_gust, wind_speed, wind_direction
# 	•	pressure
# 	•	cloud_cover
# 	•	visibility
# 	•	solar_radiation, solar_energy
# 	•	uv_index
# 	•	conditions
# 	•	description
#
# Location Data
#
# 	•	latitude, longitude
# 	•	latitude_start, longitude_start, latitude_end, longitude_end
# 	•	resolved_address, address
# 	•	mid_latitude, mid_longitude
# 	•	neighbourhood, quarter, district
#
# Parking Data
#
# 	•	id_tram
# 	•	places
# 	•	current_status
# 	•	predicted_status
# 	•	tariff_id, tariff_code, tariff_description, short_tariff_description, max_time, min_time
# 	•	schedule_id, schedule_code, schedule_description, short_schedule_description
# 	•	section_type, section_components

# Traffic Data
#
# 	•	current_status

# 2. Fields for Clustering High Traffic + Worst Weather
#
# For clustering to assign high traffic and adverse weather conditions, we can use the following fields:
#
# Traffic Indicators
#
# 	•	current_status
#
# Weather Indicators
#
# 	•	precipitation, precip_probability, precip_coverage
# 	•	snow, snow_depth
# 	•	wind_gust, wind_speed
# 	•	visibility
# 	•	conditions (categorical field can be encoded for clustering)
#
# Temporal Indicators
#
# 	•	datetime (for time-based clustering)
# 	•	day_of_week


df_clustering = df[
    [
        "places",
        "neighbourhood_bcn",
        "district",
        "current_status",
        "precipitation",
        "precip_probability",
        "precip_coverage",
        "temp",
        "snow",
        "snow_depth",
        "wind_gust",
        "visibility",
        "cloud_cover",
        "conditions",
        "day_of_week",
        "month",
        "day",
        "is_weekend",
        "year",
    ]
]


mean_per_neighbourhood = df_clustering.groupby("neighbourhood_bcn")[
    "current_status"
].transform("mean")
mean_per_neighbourhood.head(5)


df_clustering["current_status"] = df_clustering["current_status"].fillna(
    mean_per_neighbourhood
)


df_encoded = pd.get_dummies(
    df_clustering,
    columns=["neighbourhood_bcn", "district", "conditions", "day_of_week"],
)


df_weight_estimation = df_encoded[
    [
        "places",
        "current_status",
        "precipitation",
        "visibility",
        "cloud_cover",
        "is_weekend",
        "snow",
        "temp",
    ]
]


scaler = MinMaxScaler()
scaled_estimation = scaler.fit_transform(df_weight_estimation)


df_scaled_weight_estimation = pd.DataFrame(
    scaled_estimation, columns=df_weight_estimation.columns
)
df_scaled_weight_estimation.head(5)


weights = {
    "places": 0.5,
    "current_status": 0.3,
    "precipitation": 0.15,
    "visibility": 0.1,
    "cloud_cover": 0.1,
    "is_weekend": 0.1,
    "snow": 0.1,
    "temp": 0.1,
}


df_scaled_weight_estimation["estimated_occupancy_rate"] = (
    df_scaled_weight_estimation[
        [
            "places",
            "current_status",
            "precipitation",
            "visibility",
            "cloud_cover",
            "is_weekend",
            "snow",
            "temp",
        ]
    ]
    .mul(weights.values())
    .sum(axis=1)
)


original_scaled_weight_estimation = scaler.inverse_transform(
    df_scaled_weight_estimation.iloc[:, :-1]
)


df_original_scaled_weight_estimation = pd.DataFrame(
    original_scaled_weight_estimation, columns=df_weight_estimation.columns
)

df_original_scaled_weight_estimation["estimated_occupancy_rate"] = (
    df_scaled_weight_estimation["estimated_occupancy_rate"]
)
