import requests

from backend.config import OPEN_METEO_URL


def fetch_realtime_uv(lat: float, lon: float):
    params = {
        "latitude": lat,
        "longitude": lon,
        "timezone": "auto",
        "current": "uv_index,temperature_2m",
    }
    response = requests.get(OPEN_METEO_URL, params=params, timeout=20)
    response.raise_for_status()
    return response.json()


def fetch_hourly_uv(lat: float, lon: float):
    params = {
        "latitude": lat,
        "longitude": lon,
        "timezone": "auto",
        "hourly": "uv_index,temperature_2m",
    }
    response = requests.get(OPEN_METEO_URL, params=params, timeout=20)
    response.raise_for_status()
    return response.json()


def fetch_weekly_uv(lat: float, lon: float):
    params = {
        "latitude": lat,
        "longitude": lon,
        "timezone": "auto",
        "daily": "uv_index_max,temperature_2m_max,temperature_2m_min",
    }
    response = requests.get(OPEN_METEO_URL, params=params, timeout=20)
    response.raise_for_status()
    return response.json()