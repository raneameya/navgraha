import pytz, re, stdout_to_pd as sp, pandas as pd
from datetime import datetime

def add_non_equi_col(p1, p2, p1col, p2col_range, p2col_get):
    '''
    Join columns from p2 to p1, based on values in p1[p1col] lying in 
    ranges specified p2[p2col_range]
    '''
    # Create list of p2's indices where the value of p1[p1col] 
    # (for each value in p1[p1col]) lies in the 
    # fractional_interval at p2.at[idx, p2col_range] 
    matched_idx = [
        p2_idx for p1_idx in p1.index.values 
                for p2_idx in p2.index.values 
                    if p2.at[p2_idx, p2col_range].isin(p1.at[p1_idx, p1col])
    ]
    # Append columns from p2 corresponding to the indices
    # These columns may contain repeated rows, so reset index
    p1[p2col_get] = p2.iloc[
        matched_idx, p2.columns.get_indexer(p2col_get)
    ].reset_index(drop = True)
    return p1

# Keep for performance testing
def add_non_equi_col_old(p1, p2, p1col, p2col_high, p2col_low, p2col_get):
    # Create column of p2's indices in p1 
    # that correspond to value between high and low
    matched_idx = p1[p1col].apply(
        lambda x: p2[(p2[p2col_low]<=x) & (x<p2[p2col_high])].index.item()
    )
    # Append columns from p2 corresponding to the indices
    # These columns may contain repeated rows, so reset index
    p1[p2col_get] = p2.iloc[
        matched_idx, p2.columns.get_indexer(p2col_get)
    ].reset_index(drop = True)
    return p1

def round_cols(p, cols, round):
    for col, rd in zip(cols, round):
        if pd.api.types.is_numeric_dtype(p[col]):
            p[col] = p[col].round(rd)
        elif pd.api.types.is_object_dtype(p[col]):
            p[col] = p[col].str.replace(
                r'(?<=\.).*', 
                # The commented lambda works in terminal, but not in function
                # lambda m: str(round(float(m.group(0)),rd)), 
                lambda m: m.group(0)[0:rd], 
                regex = True
            )
    return p

def lunar_phases(sweedir, dt, tz):
    # Point to where the ephemeris data files live
    edir=sweedir + 'ephe'
    # Binary to run, in this case swetest
    binary=[sweedir + 'swetest']
    # These arguments won't be exposed to the user    
    common_args=['-p1', '-head', '-edir' + edir, '-g ']
    # Read stdout of swetest as dataframe
    phases=sp.read_stdout(
        cmd=' '.join(
            binary+common_args+['-d0', '-n3000', '-s15m', '-fPTl']+
            birth_datetime_args(dt)
        ), reader='table', sep='\t', col_names=['Graha', 'Datetime', 'Phase']
    )
    phases=phases[['Datetime', 'Phase']]
    # Convert string to datetime. todo:Are UT & UTC same?
    phases['Datetime']=pd.to_datetime(
        phases['Datetime'].str.replace('UT', 'UTC'), 
        format='%d.%m.%Y %H:%M:%S %Z'
    )
    # Create local timezone object
    local_tz=pytz.timezone(tz)
    # Convert to local timezone
    phases['Datetime']=phases['Datetime'].apply(
        lambda x: x.astimezone(local_tz)
    )
    return phases

def cyclic_shift(x, start: int):
    if isinstance(x, list):
        len_x = len(x)
        cyclic_idx = [
            ((start + i) % len_x) 
            for i in range(len_x)
        ]
        return [x[i] for i in cyclic_idx]
    elif isinstance(x, dict):
        keylist = list(x.keys())
        cyclic_idx = cyclic_shift(x = keylist, start = start)
        return {k:x[k] for k in cyclic_idx}

def chart_kwargs(chart, dt:datetime, ay = None):
    '''
    Returns a dictionary mapping the arguments to create a new chart with 
    the specified datetime, at the same place as the input chart. This is 
    useful to calculate a tajaka based on the original chart
    '''
    if ay is None:
        ay = chart.ayanamsa
    kwarg_dict = {
        'b_yr': dt.year,
        'b_mo': dt.month,
        'b_da': dt.day,
        'b_hr': dt.hour,
        'b_mi': dt.minute,
        'b_sc': dt.second,
        'b_lon': chart.lon,
        'b_lat': chart.lat,
        'b_tz': chart.tz, 
        'ay': ay,
        'place': chart.place
    }
    return kwarg_dict

def read_txt_file(path):
    with open(path, 'r') as file:
        txt = file.read()
    return txt

def dms(degrees: float):
    degrees = degrees % 360
    deg = int((degrees % 30) // 1)
    min = int((60 * (degrees % 1)) // 1)
    sec = 60 * ((60 * (degrees % 1)) % 1)
    out = f'{deg}°{min}\'{sec:.1f}'
    return out
