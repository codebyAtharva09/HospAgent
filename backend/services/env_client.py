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
        Returns a structured dict with env data or error info.
        """
        lat = lat or self.default_lat
        lon = lon or self.default_lon

        if not self.api_key:
            print("Warning: Missing OPENWEATHER_API_KEY. Returning mock data.")
            return self._get_fallback_data("Missing API Key")

        async with httpx.AsyncClient() as client:
            try:
                weather_task = client.get(
                    f"{self.base_url}/weather",
                    params={"lat": lat, "lon": lon, "appid": self.api_key, "units": "metric"},
                    timeout=10.0
                )
                pollution_task = client.get(
                    f"{self.base_url}/air_pollution",
                    params={"lat": lat, "lon": lon, "appid": self.api_key},
                    timeout=10.0
                )

                weather_res, pollution_res = await asyncio.gather(weather_task, pollution_task, return_exceptions=True)

                # Check for network/protocol errors
                if isinstance(weather_res, Exception) or isinstance(pollution_res, Exception):
                    print(f"Network Error: Weather={weather_res}, Pollution={pollution_res}")
                    return self._get_fallback_data("Network Error")

                if weather_res.status_code != 200 or pollution_res.status_code != 200:
                    print(f"API Error: Weather={weather_res.status_code}, Pollution={pollution_res.status_code}")
                    return self._get_fallback_data(f"API Error: W={weather_res.status_code} P={pollution_res.status_code}")

                weather_data = weather_res.json()
                pollution_data = pollution_res.json()

                return self._process_response(weather_data, pollution_data)

            except Exception as e:
                print(f"Exception fetching live env data: {e}")
                return self._get_fallback_data(str(e))

    def _get_fallback_data(self, error_msg: str):
        """
        Return a safe fallback structure so the UI doesn't crash.
        """
        return {
            "status": "unavailable",
            "error": error_msg,
            "location": {"name": "Mumbai (Offline)", "lat": self.default_lat, "lon": self.default_lon},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "last_updated_utc": datetime.now(timezone.utc).isoformat(),
            "temperature_c": 28.0, # Default fallback
            "temp_c": 28.0, # Alias for frontend
            "humidity": 60,
            "weather": "Haze",
            "weather_desc": "Haze (Offline)",
            "weather_label": "Haze (Offline)", # Alias for frontend
            "aqi": 150,
            "aqi_index_1_5": 3,
            "aqi_number": 150,
            "pm25": 55.0,
            "pollutants": {
                "pm2_5": 55.0,
                "pm10": 120.0,
                "no2": 20.0,
                "so2": 10.0,
                "o3": 30.0,
                "co": 500.0
            }
        }

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
        aqi_index = p_list.get("main", {}).get("aqi", 3) # 1-5
        
        pm25 = components.get("pm2_5", 0)
        pm10 = components.get("pm10", 0)
        aqi_number = self.compute_aqi_number(pm25, pm10)

        # Use current time to reflect the polling freshness
        last_updated = datetime.now(timezone.utc).isoformat()
        
        weather_desc = weather.get("weather", [{}])[0].get("description", "clear")

        return {
            "status": "ok",
            "location": {
                "lat": weather.get("coord", {}).get("lat"),
                "lon": weather.get("coord", {}).get("lon"),
                "name": weather.get("name", "Goregaon, Mumbai")
            },
            "timestamp": last_updated,
            "last_updated_utc": last_updated,
            "temperature_c": weather.get("main", {}).get("temp"),
            "temp_c": weather.get("main", {}).get("temp"), # Alias for frontend
            "humidity": weather.get("main", {}).get("humidity"),
            "weather_desc": weather_desc,
            "weather": weather_desc, 
            "weather_label": weather_desc, # Alias for frontend
            "aqi_index_1_5": aqi_index,
            "aqi_number": aqi_number,
            "aqi": aqi_number, # Alias for frontend
            "pm25": pm25, # Alias for frontend
            "pollutants": {
                "pm2_5": pm25,
                "pm10": pm10,
                "no2": components.get("no2"),
                "so2": components.get("so2"),
                "o3": components.get("o3"),
                "co": components.get("co")
            }
        }
