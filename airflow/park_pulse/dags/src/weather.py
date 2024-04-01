import requests


class OpenWeather:
    def __init__(self, api_key, q="Barcelona,Spain") -> None:
        self.api_key = api_key
        self.q = q

    def __str__(self) -> str:
        pass

    def get_weather():
        url = f"http://api.openweathermap.org/data/2.5/weather?q={self.q}&APPID={self.api_key}"
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        return data

    def get_weather_data(df):
        result = []
        for i in df.index:
            row = df.iloc[i]
            date = row["date"]
            base_url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": "Barcelona,spain",  # City and country code
                "appid": api_key,
                "dt": int(
                    pd.to_datetime(date).timestamp()
                ),  # Convert date to timestamp
            }
            # print(params)
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                data = pd.json_normalize(response.json())
                data["id"] = weather_data["weather"][0][0].get("id")
                data["main"] = weather_data["weather"][0][0].get("main")
                data["description"] = weather_data["weather"][0][0].get("description")
                data.drop(columns=["weather"], inplace=True)
                # print(json.dumps(response.json()))
                result.append(data)
            else:
                continue
        df = pd.concat(result)
        return df
