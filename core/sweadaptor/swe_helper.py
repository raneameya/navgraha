from datetime import datetime
from zoneinfo import ZoneInfo
import ctypes
from ctypes import c_int, c_double, c_char_p, POINTER

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

# Define the argument types for the function
lib.planet_info_arr.argtypes = [
    POINTER(c_int),    # ipl_arr[]
    c_int,             # n_planets
    c_int,             # year
    c_int,             # month
    c_int,             # day
    c_int,             # hour
    c_int,             # min
    c_double,          # sec
    c_int,             # sid_mode
    c_double,          # lon
    c_double,          # lat
    c_char_p,          # ephe_path
    POINTER(c_double), # lon_arr[]
    POINTER(c_double)  # speed_arr[]
]

# Define the return type (void)
lib.planet_info_arr.restype = None


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

def get_planet_info_arr(
    planets: list[str], 
    dt: datetime, 
    lat: float = 0, 
    lon: float = 0, 
    ay: str = 'True Citra'
) -> tuple(float, float):
    planet_ints = [int(graha_dict[graha][0]) for graha in graha_dict]
    n_planets = len(planets)
    ay_id = int(ayanamsa_dict[ay])
    utc_dt = dt.astimezone(ZoneInfo('UTC'))

    # Create the output arrays
    ipl_arr = (c_int * n_planets)(*planet_ints)
    lon_results = (c_double * n_planets)()
    speed_results = (c_double * n_planets)()

    # Call the function
    lib.planet_info_arr(
        ipl_arr, n_planets, utc_dt.year, utc_dt.month, utc_dt.day, 
        utc_dt.hour, utc_dt.minute, utc_dt.second, ay_id, lon, lat, 
        ephemeris_path, lon_results, speed_results
    )

    # Convert results back to standard Python lists
    longitudes = list(lon_results)
    speeds = list(speed_results)
    return (longitudes, speeds)