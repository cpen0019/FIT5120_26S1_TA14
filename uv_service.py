from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Callable
from urllib.error import HTTPError
from urllib.parse import urlencode, urlparse
from urllib.request import urlopen


DEFAULT_URL = "https://api.open-meteo.com/v1/forecast"
DEFAULT_POSTCODE = "3000"
DEFAULT_FORECAST_DAYS = 7
DEFAULT_SQL_PATH = Path(__file__).with_name("australian-postcodes.sql")

CURRENT_FIELDS = ["uv_index", "temperature_2m", "cloud_cover", "relative_humidity_2m"]
HOURLY_FIELDS = ["uv_index", "temperature_2m", "cloud_cover", "relative_humidity_2m"]
DAILY_FIELDS = ["sunrise", "sunset", "uv_index_max", "temperature_2m_max", "temperature_2m_min"]

STATE_TIMEZONES = {
    "NSW": "Australia/Sydney",
    "VIC": "Australia/Melbourne",
    "QLD": "Australia/Brisbane",
    "WA": "Australia/Perth",
    "SA": "Australia/Adelaide",
    "ACT": "Australia/Sydney",
    "TAS": "Australia/Hobart",
    "NT": "Australia/Darwin",
}

CAPITAL_CITY_LOCATIONS = [
    {
        "postcode": "2000",
        "city": "Sydney",
        "state": "NSW",
        "latitude": -33.875,
        "longitude": 151.125,
        "timezone": "Australia/Sydney",
    },
    {
        "postcode": "3000",
        "city": "Melbourne",
        "state": "VIC",
        "latitude": -37.8136,
        "longitude": 144.9631,
        "timezone": "Australia/Melbourne",
    },
    {
        "postcode": "4000",
        "city": "Brisbane",
        "state": "QLD",
        "latitude": -27.4698,
        "longitude": 153.0251,
        "timezone": "Australia/Brisbane",
    },
    {
        "postcode": "6000",
        "city": "Perth",
        "state": "WA",
        "latitude": -31.9505,
        "longitude": 115.8605,
        "timezone": "Australia/Perth",
    },
    {
        "postcode": "5000",
        "city": "Adelaide",
        "state": "SA",
        "latitude": -34.9285,
        "longitude": 138.6007,
        "timezone": "Australia/Adelaide",
    },
    {
        "postcode": "2600",
        "city": "Canberra",
        "state": "ACT",
        "latitude": -35.2809,
        "longitude": 149.13,
        "timezone": "Australia/Sydney",
    },
    {
        "postcode": "7000",
        "city": "Hobart",
        "state": "TAS",
        "latitude": -42.8821,
        "longitude": 147.3272,
        "timezone": "Australia/Hobart",
    },
    {
        "postcode": "0800",
        "city": "Darwin",
        "state": "NT",
        "latitude": -12.4634,
        "longitude": 130.8456,
        "timezone": "Australia/Darwin",
    },
]


class PostcodeNotFoundError(LookupError):
    pass


@dataclass(frozen=True)
class LocationRecord:
    postcode: str
    city: str
    state: str
    latitude: float
    longitude: float
    timezone: str

    @property
    def region_id(self) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", self.city.lower()).strip("-")
        return f"{self.postcode}-{slug}-{self.state.lower()}"


def should_send_api_key(api_url: str) -> bool:
    hostname = (urlparse(api_url).hostname or "").lower()
    return hostname.startswith("customer-")


def normalize_postcode(postcode: str | None) -> str:
    value = (postcode or "").strip()
    if not value:
        return DEFAULT_POSTCODE
    if value.isdigit() and len(value) <= 4:
        return value.zfill(4)
    return value


def infer_timezone(state: str) -> str:
    return STATE_TIMEZONES.get(state, "Australia/Melbourne")


def parse_postcodes_sql(sql_text: str) -> dict[str, LocationRecord]:
    pattern = re.compile(
        r"\('(?P<postcode>[^']*)',\s*'(?P<suburb>[^']*)',\s*'(?P<state>[^']*)',\s*(?P<latitude>-?\d+(?:\.\d+)?),\s*(?P<longitude>-?\d+(?:\.\d+)?)\)"
    )

    records: dict[str, LocationRecord] = {}
    for match in pattern.finditer(sql_text):
        postcode = match.group("postcode")
        if postcode in records:
            continue
        state = match.group("state")
        records[postcode] = LocationRecord(
            postcode=postcode,
            city=match.group("suburb"),
            state=state,
            latitude=float(match.group("latitude")),
            longitude=float(match.group("longitude")),
            timezone=infer_timezone(state),
        )
    return records


@lru_cache(maxsize=4)
def load_postcode_map(sql_path: str = str(DEFAULT_SQL_PATH)) -> dict[str, LocationRecord]:
    sql_file = Path(sql_path)
    sql_text = sql_file.read_text(encoding="utf-8")
    return parse_postcodes_sql(sql_text)


def resolve_location(postcode: str | None, sql_path: str = str(DEFAULT_SQL_PATH)) -> LocationRecord:
    normalized = normalize_postcode(postcode)
    postcode_map = load_postcode_map(sql_path)
    try:
        return postcode_map[normalized]
    except KeyError as exc:
        raise PostcodeNotFoundError(f"Postcode '{normalized}' was not found.") from exc


def build_params(
    latitude: float,
    longitude: float,
    timezone: str,
    forecast_days: int,
    current: list[str] | None = None,
    hourly: list[str] | None = None,
    daily: list[str] | None = None,
) -> dict[str, str | float | int]:
    params: dict[str, str | float | int] = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone,
        "forecast_days": forecast_days,
    }
    if current:
        params["current"] = ",".join(current)
    if hourly:
        params["hourly"] = ",".join(hourly)
    if daily:
        params["daily"] = ",".join(daily)
    return params


def fetch_open_meteo_data(
    latitude: float,
    longitude: float,
    timezone: str,
    forecast_days: int = DEFAULT_FORECAST_DAYS,
    current: list[str] | None = None,
    hourly: list[str] | None = None,
    daily: list[str] | None = None,
) -> dict:
    api_url = os.getenv("OPEN_METEO_URL", DEFAULT_URL)
    api_key = os.getenv("OPEN_METEO_API_KEY")
    params = build_params(
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
        forecast_days=forecast_days,
        current=current,
        hourly=hourly,
        daily=daily,
    )

    if api_key and should_send_api_key(api_url):
        params["apikey"] = api_key

    request_url = f"{api_url}?{urlencode(params)}"
    try:
        with urlopen(request_url, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            "Open-Meteo request failed with "
            f"HTTP {exc.code}. URL: {request_url}\nResponse: {details}"
        ) from exc


def risk_category(uv_index: float | int | None) -> str | None:
    if uv_index is None:
        return None
    value = float(uv_index)
    if value <= 2:
        return "Low"
    if value <= 5:
        return "Moderate"
    if value <= 7:
        return "High"
    if value <= 10:
        return "Very High"
    return "Extreme"


def map_realtime(location: LocationRecord, payload: dict) -> dict[str, object]:
    current = payload.get("current", {})
    timezone = payload.get("timezone") or location.timezone
    uv_index = current.get("uv_index")
    return {
        "region_id": location.region_id,
        "city": location.city,
        "state": location.state,
        "latitude": payload.get("latitude", location.latitude),
        "longitude": payload.get("longitude", location.longitude),
        "timezone": timezone,
        "datetime": current.get("time"),
        "uv_index": uv_index,
        "temperature": current.get("temperature_2m"),
        "cloud_cover": current.get("cloud_cover"),
        "relative_humidity": current.get("relative_humidity_2m"),
        "risk_category": risk_category(uv_index),
    }


def map_hourly(location: LocationRecord, payload: dict) -> list[dict[str, object]]:
    hourly = payload.get("hourly", {})
    timestamps = hourly.get("time", [])
    rows: list[dict[str, object]] = []
    for index, timestamp in enumerate(timestamps):
        uv_index = _value_at(hourly.get("uv_index", []), index)
        rows.append(
            {
                "region_id": location.region_id,
                "datetime": timestamp,
                "uv_index": uv_index,
                "temperature": _value_at(hourly.get("temperature_2m", []), index),
                "cloud_cover": _value_at(hourly.get("cloud_cover", []), index),
                "relative_humidity": _value_at(hourly.get("relative_humidity_2m", []), index),
                "risk_category": risk_category(uv_index),
            }
        )
    return rows


def map_weekly(location: LocationRecord, payload: dict) -> list[dict[str, object]]:
    daily = payload.get("daily", {})
    dates = daily.get("time", [])
    rows: list[dict[str, object]] = []
    for index, date_value in enumerate(dates):
        rows.append(
            {
                "region_id": location.region_id,
                "date": date_value,
                "sunrise": _value_at(daily.get("sunrise", []), index),
                "sunset": _value_at(daily.get("sunset", []), index),
                "uv_index_max": _value_at(daily.get("uv_index_max", []), index),
                "temperature_max": _value_at(daily.get("temperature_2m_max", []), index),
                "temperature_min": _value_at(daily.get("temperature_2m_min", []), index),
            }
        )
    return rows


def map_citywise(location: LocationRecord, payload: dict) -> dict[str, object]:
    current = map_realtime(location, payload)
    return {
        "postcode": location.postcode,
        "city": location.city,
        "state": location.state,
        "latitude": current["latitude"],
        "longitude": current["longitude"],
        "timezone": current["timezone"],
        "datetime": current["datetime"],
        "uv_index": current["uv_index"],
        "temperature": current["temperature"],
        "cloud_cover": current["cloud_cover"],
        "relative_humidity": current["relative_humidity"],
        "risk_category": current["risk_category"],
    }


def get_realtime_uv(
    postcode: str | None = None,
    sql_path: str = str(DEFAULT_SQL_PATH),
    fetcher: Callable[..., dict] = fetch_open_meteo_data,
) -> dict[str, object]:
    location = resolve_location(postcode, sql_path)
    payload = fetcher(
        latitude=location.latitude,
        longitude=location.longitude,
        timezone=location.timezone,
        forecast_days=1,
        current=CURRENT_FIELDS,
    )
    return map_realtime(location, payload)


def get_hourly_forecast(
    postcode: str | None = None,
    sql_path: str = str(DEFAULT_SQL_PATH),
    fetcher: Callable[..., dict] = fetch_open_meteo_data,
) -> list[dict[str, object]]:
    location = resolve_location(postcode, sql_path)
    payload = fetcher(
        latitude=location.latitude,
        longitude=location.longitude,
        timezone=location.timezone,
        forecast_days=1,
        hourly=HOURLY_FIELDS,
    )
    return map_hourly(location, payload)


def get_weekly_forecast(
    postcode: str | None = None,
    sql_path: str = str(DEFAULT_SQL_PATH),
    fetcher: Callable[..., dict] = fetch_open_meteo_data,
) -> list[dict[str, object]]:
    location = resolve_location(postcode, sql_path)
    payload = fetcher(
        latitude=location.latitude,
        longitude=location.longitude,
        timezone=location.timezone,
        forecast_days=DEFAULT_FORECAST_DAYS,
        daily=DAILY_FIELDS,
    )
    return map_weekly(location, payload)


def get_citywise_uv(fetcher: Callable[..., dict] = fetch_open_meteo_data) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for city in CAPITAL_CITY_LOCATIONS:
        location = LocationRecord(
            postcode=city["postcode"],
            city=city["city"],
            state=city["state"],
            latitude=city["latitude"],
            longitude=city["longitude"],
            timezone=city["timezone"],
        )
        payload = fetcher(
            latitude=location.latitude,
            longitude=location.longitude,
            timezone=location.timezone,
            forecast_days=1,
            current=CURRENT_FIELDS,
        )
        rows.append(map_citywise(location, payload))
    return rows


def _value_at(values: list[object], index: int) -> object | None:
    if index < len(values):
        return values[index]
    return None
