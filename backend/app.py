from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests

from backend.cancer_queries import get_cancer_trends, get_cancer_age_groups
from backend.map_queries import get_state_stats, get_state_details, get_state_comparison
from backend.uv_service import fetch_realtime_uv, fetch_hourly_uv, fetch_weekly_uv

app = FastAPI(title="UV Guardian API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "UV Guardian API is running",
        "available_endpoints": [
            "/api/health",
            "/api/uv/realtime?lat=-37.8136&lon=144.9631",
            "/api/uv/hourly?lat=-37.8136&lon=144.9631",
            "/api/uv/weekly?lat=-37.8136&lon=144.9631",
            "/api/cancer/trends",
            "/api/cancer/age-groups",
            "/api/map/states",
            "/api/map/state/VIC",
            "/api/map/state/Victoria",
            "/api/map/compare",
        ],
    }


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/uv/realtime")
def realtime_uv(lat: float, lon: float):
    try:
        return fetch_realtime_uv(lat, lon)
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch realtime UV: {str(e)}")


@app.get("/api/uv/hourly")
def hourly_uv(lat: float, lon: float):
    try:
        return fetch_hourly_uv(lat, lon)
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch hourly UV: {str(e)}")


@app.get("/api/uv/weekly")
def weekly_uv(lat: float, lon: float):
    try:
        return fetch_weekly_uv(lat, lon)
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch weekly UV: {str(e)}")


@app.get("/api/cancer/trends")
def cancer_trends():
    try:
        return get_cancer_trends()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch cancer trends: {str(e)}")


@app.get("/api/cancer/age-groups")
def cancer_age_groups():
    try:
        return get_cancer_age_groups()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch cancer age groups: {str(e)}")


@app.get("/api/map/states")
def map_states():
    try:
        return get_state_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch state stats: {str(e)}")


@app.get("/api/map/state/{state_code}")
def map_state_details(state_code: str):
    try:
        return get_state_details(state_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch state details: {str(e)}")


@app.get("/api/map/compare")
def map_compare():
    try:
        return get_state_comparison()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch map comparison data: {str(e)}")