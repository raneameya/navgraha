import datetime as dt
import misc_functions as mf
import chart as crt

def get_sun_lon(chart:crt.chart):
    df = chart.placements
    return df['Lon'][df['Graha'] == 'Sun'].squeeze()

def sol_cross(
    yr:int, 
    birth_crt:crt.chart,
    tropical:bool,
    yr_len:float = 365.25
):
    # Estimated datetime at when longitides of Sun in the given year are 
    # equal to the longitudes of the Sun in the birth year
    year_delta = yr - birth_crt.datetime.year
    # Add 182 so initial estimate is about midway between birthday of 
    # yr and birthday of (yr - 1)
    init_datetime = birth_crt.datetime + dt.timedelta(
        days = ((year_delta - 1) * yr_len) + 182
    )
    if tropical:
        tropical_birth_chart_args = mf.chart_kwargs(
            chart = birth_crt, dt = birth_crt.datetime, ay = ''
        )
        target_lon = get_sun_lon(crt.chart(**tropical_birth_chart_args))
        chart_args = mf.chart_kwargs(
            chart = birth_crt, dt = init_datetime, ay = ''
        )
    else:
        chart_args = mf.chart_kwargs(chart = birth_crt, dt = init_datetime)
        target_lon = get_sun_lon(birth_crt)
    init_lon = get_sun_lon(crt.chart(**chart_args))
    # Account for targets being "behind" init lon as per 0 point
    if target_lon < init_lon:
        target_lon = target_lon + 360
    # Degrees/avg. solar speed in deg/day
    estimated_days = (target_lon - init_lon - 3) / (360/365.2425)
    td = dt.timedelta(days = estimated_days)
    loop_dt = init_datetime + td    
    deg_delta = 10000
    loop_num = 0
    loop_lon = 0
    print(f'target_lon:{target_lon%360}')
    while abs(deg_delta) > 0.000001:
        if tropical:
            chart_args = mf.chart_kwargs(chart = birth_crt, dt = loop_dt, ay = '')        
        else:
            chart_args = mf.chart_kwargs(chart = birth_crt, dt = loop_dt)
        loop_lon = get_sun_lon(crt.chart(**chart_args))        
        deg_delta = (target_lon%360) - loop_lon
        loop_td = dt.timedelta(days = deg_delta/(360/365))
        loop_dt = loop_dt + loop_td
        loop_num = loop_num + 1
        # Generally good enough estimate 10 loops in
        if loop_num > 10:
            break
    return loop_dt
