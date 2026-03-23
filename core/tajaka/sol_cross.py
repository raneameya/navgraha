import datetime as dt
import core.misc.misc_functions as mf
import core.chart.chart as crt
from core.tajaka.get_sun_lon import get_sun_lon

def sol_cross(
    yr:int, 
    birth_crt:crt.chart,
    tropical:bool,
    yr_len:float = 365.25
):
    # Estimated datetime at when longitides of Sun in the given year are 
    # equal to the longitudes of the Sun in the birth year
    year_delta = yr - birth_crt.birth_event.dt.year
    # Add 182 so initial estimate is about midway between birthday of 
    # yr and birthday of (yr - 1)
    init_datetime = birth_crt.birth_event.dt + dt.timedelta(
        days = ((year_delta - 1) * yr_len) + 182
    )
    # Birth chart ayanamsa
    b_ay = birth_crt.swisseph_adaptor.ayanamsa
    if tropical:
        target_lon = get_sun_lon(dt = birth_crt.birth_event.dt, ay = 'Tropical', tropical = True)
        init_lon = get_sun_lon(dt = init_datetime, ay = 'Tropical', tropical = True)
    else:
        target_lon = get_sun_lon(dt = birth_crt.birth_event.dt, ay = b_ay, tropical = False)
        init_lon = get_sun_lon(dt = init_datetime, ay = b_ay, tropical = False)
    # Account for targets being "behind" init lon as per 0 point (i.e. 0° Aries)
    if target_lon < init_lon:
        target_lon = target_lon + 360
    # Degrees/avg. solar speed in deg/day
    estimated_days = (target_lon - init_lon - 3) / (360/365.2425)
    td = dt.timedelta(days = estimated_days)
    loop_dt = init_datetime + td
    deg_delta = 10000
    loop_num = 0
    loop_lon = 0
    while abs(deg_delta) > 0.000001:
        if tropical:
            loop_lon = get_sun_lon(dt = loop_dt, ay = 'Tropical', tropical = True)
        else:
            loop_lon = get_sun_lon(dt = loop_dt, ay = b_ay, tropical = False)
        deg_delta = (target_lon%360) - loop_lon
        loop_td = dt.timedelta(days = deg_delta/(360/365))
        loop_dt = loop_dt + loop_td
        loop_num = loop_num + 1
        # Generally good enough estimate 10 loops in
        if loop_num > 10:
            break
    return loop_dt
