import re
from datetime import datetime

import pandas as pd

from core.misc.misc_functions import add_non_equi_col
import core.chart.chart as crt
from core.chart.chart_minimal import chart_minimal
from core.divisionals.divisional_helpers import add_house
from core.sweadaptor.swisseph_adaptor import SwissEphAdaptor
from core.sweadaptor.swe_helper import get_planet_info, get_planet_info_arr
from core.data.constants import graha_dict, rnp
from core.misc.misc_functions import dms

def d1(birth_crt: crt.chart) -> chart_minimal:
    p = swetest(adapter = birth_crt.swisseph_adaptor)
    # Add other details
    add_cols = ['Rāśi', 'Nakṣatra', 'Graha devatā', 'Pada', 'Puṣkara']
    p = add_non_equi_col(
        p1 = p,
        p2 = rnp,
        p1col = 'Lon',
        p2col_range = 'Degrees',
        p2col_get = add_cols
    )
    # Reorder columns
    p = p[[
        'Birth', 'Graha', 'Lon', 'Lon°', 'Lon30', 'Speed', 'Sign', 
        'Bhava', 'Rāśi', 'Nakṣatra', 'Graha devatā', 'Pada', 'Puṣkara'
    ]]
    return chart_minimal(
        placements = p, 
        display_cols = [
            'Graha', 'Lon°', 'Nakṣatra', 'Graha devatā', 
            'Pada', 'Puṣkara', 'Speed'
        ]
    )

def swetest(adapter: SwissEphAdaptor):
    birth_datetime = adapter.birth_event.dt
    latitude = adapter.birth_event.latitude
    longitude = adapter.birth_event.longitude
    ayanamsa = adapter.ayanamsa
    lon_speeds = get_planet_info_arr(
        planets = list(graha_dict.keys()), dt = birth_datetime, 
        lat = latitude, lon = longitude, ay = ayanamsa
    )
    p = {
        'Birth': birth_datetime.strftime('%Y-%m-%d %H:%M:%S %Z(%z)'),
        'Graha': list(graha_dict.keys()), 
        'Lon': lon_speeds[0], 
        'Speed': lon_speeds[1]
    }
    p = pd.DataFrame(data = p, columns = ['Birth', 'Graha', 'Lon', 'Speed'])
    # Replace total degrees by degrees in house/sign
    p['Lon°'] = p['Lon'].apply(lambda x: dms(x))
    # Sign and House calculation
    p = add_house(p)
    # Add degrees in house as a numeric
    p['Lon30'] = p['Lon'].apply(lambda x: x%30)
    return p
