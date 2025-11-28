import httpx
import os
import asyncio
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

class EnvironmentClient:
    """
    Client for fetching live environmental data from OpenWeather API.
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5"
        # Default to Mumbai (Goregaon)
        self.default_lat = 19.155
        self.default_lon = 72.849

    async def get_live_data(self, lat=None, lon=None):
        """
        Fetch both Weather and Air Pollution data concurrently.
        """
        if not self.api_key:
            # Fallback only if API key is missing, but preferably should error out as per instructions.
            # However, user said "If OpenWeather fails, return HTTP 502".
            # For missing key, we can raise an error or return a specific error dict.
            raise Exception("Missing OPENWEATHER_API_KEY")

        lat = lat or self.default_lat
        lon = lon or self.default_lon

        async with httpx.AsyncClient() as client:
            try:
                weather_task = client.get(
                    f"{self.base_url}/weather",
                    params={"lat": lat, "lon": lon, "appid": self.api_key, "units": "metric"}
                )
                pollution_task = client.get(
                    f"{self.base_url}/air_pollution",
                    params={"lat": lat, "lon": lon, "appid": self.api_key}
                )

                weather_res, pollution_res = await asyncio.gather(weather_task, pollution_task)

                if weather_res.status_code != 200 or pollution_res.status_code != 200:
                    print(f"API Error: Weather={weather_res.status_code}, Pollution={pollution_res.status_code}")
                    raise Exception(f"OpenWeather API failed: Weather={weather_res.status_code}, Pollution={pollution_res.status_code}")

                weather_data = weather_res.json()
                pollution_data = pollution_res.json()

                return self._process_response(weather_data, pollution_data)

            except Exception as e:
                print(f"Exception fetching live env data: {e}")
                raise e

    def calc_aqi_from_pm(self, conc, breakpoints):
        for (clo, chi, ilo, ihi) in breakpoints:
            if clo <= conc <= chi:
                return round((ihi - ilo) / (chi - clo) * (conc - clo) + ilo)
        return 500  # cap

    def compute_aqi_number(self, pm25: float, pm10: float) -> int:
        PM25_BREAKPOINTS = [
            (0.0, 12.0, 0, 50),
            (12.1, 35.4, 51, 100),
            (35.5, 55.4, 101, 150),
            (55.5, 150.4, 151, 200),
            (150.5, 250.4, 201, 300),
            (250.5, 350.4, 301, 400),
            (350.5, 500.4, 401, 500),
        ]

        PM10_BREAKPOINTS = [
            (0, 54, 0, 50),
            (55, 154, 51, 100),
            (155, 254, 101, 150),
            (255, 354, 151, 200),
            (355, 424, 201, 300),
            (425, 504, 301, 400),
            (505, 604, 401, 500),
        ]
        
        aqi_pm25 = self.calc_aqi_from_pm(pm25, PM25_BREAKPOINTS)
        aqi_pm10 = self.calc_aqi_from_pm(pm10, PM10_BREAKPOINTS)
        return max(aqi_pm25, aqi_pm10)

    def _process_response(self, weather, pollution):
        """
        Merge and clean the API responses.
        """
        # Pollution data
        p_list = pollution.get("list", [{}])[0]
        components = p_list.get("components", {})
        aqi_index = p_list.get("main", {}).get("aqi", 1) # 1-5
        
        pm25 = components.get("pm2_5", 0)
        pm10 = components.get("pm10", 0)
        aqi_number = self.compute_aqi_number(pm25, pm10)

        print(f"[ENV] pm2.5={pm25}, pm10={pm10}, aqi_number={aqi_number}, index={aqi_index}")

        # Use current time to reflect the polling freshness
        last_updated = datetime.now(timezone.utc).isoformat()
        # if 'dt' in weather:
        #     last_updated = datetime.fromtimestamp(weather['dt'], timezone.utc).isoformat()

        return {
            "location": {
                "lat": weather.get("coord", {}).get("lat"),
                "lon": weather.get("coord", {}).get("lon"),
                "name": "Goregaon, Mumbai" # Hardcoded as per request or use weather.get("name")
            },
            "timestamp": last_updated, # Keep for backward compatibility if needed, but prefer last_updated_utc
            "last_updated_utc": last_updated,
            "temperature_c": weather.get("main", {}).get("temp"),
            "humidity": weather.get("main", {}).get("humidity"),
            "weather_desc": weather.get("weather", [{}])[0].get("description", "clear"),
            "aqi_index_1_5": aqi_index,
            "aqi_number": aqi_number,
            "pollutants": {
                "pm2_5": pm25,
                "pm10": pm10,
                "no2": components.get("no2"),
                "so2": components.get("so2"),
                "o3": components.get("o3"),
                "co": components.get("co")
            }
        }
