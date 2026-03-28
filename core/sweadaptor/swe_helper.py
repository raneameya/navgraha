from datetime import datetime
from zoneinfo import ZoneInfo
import ctypes

from core.data.constants import ayanamsa_dict, graha_dict

ephemeris_path = './swisseph-master/ephe'.encode('utf-8')

lib = ctypes.CDLL("./swisseph-master/swe_simple.so")

lib.planet_info.argtypes = [
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, 
    ctypes.c_double, ctypes.c_int, ctypes.c_int, ctypes.c_double, 
    ctypes.c_double, ctypes.c_int, ctypes.c_char_p
]
lib.planet_info.restype = ctypes.c_double

lib.sun_lon.argtypes = [
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, 
    ctypes.c_double, ctypes.c_int, ctypes.c_char_p
]
lib.sun_lon.restype = ctypes.c_double

def get_planet_info(
    planet:str, 
    dt: datetime, 
    lat: float = 0, 
    lon: float = 0, 
    ay: str = 'True Citra'
) -> tuple(float, float):
    pl_id = int(graha_dict[planet][0])
    ay_id = int(ayanamsa_dict[ay])
    utc_dt = dt.astimezone(ZoneInfo('UTC'))
    planet_lon = lib.planet_info(
        utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour, utc_dt.minute,
        utc_dt.second, pl_id, ay_id, lon, lat, 0, ephemeris_path
    )
    speed = lib.planet_info(
        utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour, utc_dt.minute,
        utc_dt.second, pl_id, ay_id, lon, lat, 1, ephemeris_path
    )
    return (planet_lon, speed)

# Fast function to get longitude of sun, as required in tajaka 
# birth datetime calcs. On 8550U time to compute datetimes for 
# 1300 years down from 3.5-3.6s (using get_planet_info) to ~2.2s.
def get_sun_lon(dt: datetime, ay:str):
    ay_id = int(ayanamsa_dict[ay])
    utc_dt = dt.astimezone(ZoneInfo('UTC'))
    lon = lib.sun_lon(
        utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour, utc_dt.minute,
        utc_dt.second, ay_id, ephemeris_path
    )
    return lon