import requests


class OpenWeather:
    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        pass

    def get_weather():
        url = "https://opendata-ajuntament.barcelona.cat/data/api/action/current_package_list_with_resources"
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        return data
