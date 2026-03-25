from datetime import datetime
from zoneinfo import ZoneInfo
import ctypes

from core.data.constants import ayanamsa_dict

lib = ctypes.CDLL("./swisseph-master/swe_simple.so")

# Define argument and return types
lib.planet_lon.argtypes = [
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, 
    ctypes.c_double, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_char_p
]
lib.planet_lon.restype = ctypes.c_double

def get_sun_lon(dt: datetime, ay: str, tropical: bool) -> float:
    if not tropical:
        ay_int = int(ayanamsa_dict[ay])
    else:
        ay_int = -1
    utc_dt = dt.astimezone(ZoneInfo('UTC'))
    lon = lib.planet_lon(
        utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour, utc_dt.minute,
        utc_dt.second, 0, int(not tropical), ay_int, './ephe'.encode('utf-8')
    )
    return lon
