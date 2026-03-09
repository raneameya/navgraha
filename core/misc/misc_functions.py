import re, core.misc.stdout_to_pd as sp, pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from core.misc.birth_event import BirthEvent
from core.sweadaptor.swisseph_adaptor import SwissEphAdaptor

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

def round_cols(
    p: pd.DataFrame, 
    col_list: list[str], 
    round_list: list[str]
) -> pd.DataFrame:
    '''
    Truncates columns in p, specified by col_list, to the precision 
    specified in round_list

    Args:
        p (pandas.DataFrame): The input DataFrame whose columns will 
            be truncated.
        col_list (list[str]): A list of columns in p
        round_list (list[str]): A list of integers specifying the precision to 
            which cols in col_list need to be truncated to.
    
    Returns:
        A truncated pandas.DataFrame
    '''
    for col, rd in zip(col_list, round_list):
        if pd.api.types.is_numeric_dtype(p[col]):
            p[col] = p[col].round(rd)
        elif col == 'Lon°':
            if rd == 0:
                l = lambda m: str(int(round(float(m.group(0)),rd)))
            elif rd > 0:
                l = lambda m: str(round(float(m.group(0)),rd))
            p[col] = p[col].str.replace(
                pat = r'(?<=\').*', 
                repl = l, 
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
    # Convert to local timezone
    phases['Datetime']=phases['Datetime'].apply(
        lambda x: x.astimezone(ZoneInfo(tz))
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
        ay = chart.sweph_adaptor.ayanamsa
    birth_event = BirthEvent(
            dt = dt.replace(tzinfo = chart.birth_event.dt.tzinfo), 
            latitude = chart.birth_event.latitude, 
            longitude = chart.birth_event.longitude, 
            z_height = chart.birth_event.z_height, 
            place = chart.birth_event.place
    )
    kwarg_dict = {
        'birth_event': birth_event,
        'sweph_adaptor': SwissEphAdaptor(
            base_path = chart.sweph_adaptor.base_path,
            binary = chart.sweph_adaptor.binary, 
            birth = birth_event,
            ayanamsa = ay,
            house = chart.sweph_adaptor.house,
            output_cols = chart.sweph_adaptor.output_cols,
            ephemeris_path = chart.sweph_adaptor.ephemeris_path
        )
    }
    return kwarg_dict

def read_txt_file(path):
    with open(path, 'r') as file:
        txt = file.read()
    return txt

def dms(degrees: float) -> str:
    '''
    Convert an absolute degree value into degrees–minutes–seconds
    within a 30° astrological house/sign.
    '''
    degrees = degrees % 360
    degree_int = int(degrees % 30)
    degree_mantissa = degrees % 1
    minutes = int(60 * degree_mantissa)
    seconds = 60 * ((60 * degree_mantissa) % 1)
    out = f'{degree_int}°{minutes}\'{seconds:.1f}'
    return out

def parse_time(timestr: str) -> time:
    h, m, *s = map(int, timestr.split(':'))
    s = s[0] if s else 0
    return (h, m, s)