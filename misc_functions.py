import pytz, re, stdout_to_pd as sp, pandas as pd
from datetime import datetime

def create_date_from_txt(yr, mo, da, hr, mi, se, tz):
    ## Somewhat complex process of timezone conversion.
    # Read here: https://stackoverflow.com/questions/6410971/python-datetime-object-show-wrong-timezone-offset
    # Need to specify initial datetime without timezone
    dt=datetime(
        year=yr,
        month=mo,
        day=da,
        hour=hr,
        minute=mi,
        second=se,
        tzinfo=None
    )
    # Create local timezone object
    local_tz=pytz.timezone(tz)
    # Then localise the initial timezoneless datetime object
    dt=local_tz.localize(dt)
    return dt

def swetest(sweedir, birth_args):
    # Point to where the ephemeris data files live
    edir=sweedir + 'ephe'
    # Binary to run, in this case swetest
    binary=[sweedir + 'swetest']
    # These arguments won't be exposed to the user 
    # (with the possible exception of planets)
    common_args=['-pp', '-head', '-edir' + edir]    
    # Ayanamsa and output columns. todo: expose ayanamsa to user
    config_args=['-sid29', '-fTPlLsBj']
    # To get ascendant, we need to specify house system to swetest
    house_args=[
        birth_args[2].replace('geopos', 'house').replace(',0', ',W')
    ]
    # Format output of swetest so that it is space delimited
    format_args=[
        '| sed -E \'s/(UT\\s\\S+)(\\s{1,2})(\\w)/\\1_\\3/g\'', 
        '| sed -E \'s/° /°/g\'', '| sed -E "s/\' /\'/g\"'
    ]
    colnames=[
        'Date', 'Time', 'tz', 'Graha', 'Lon', 'Lon°', 'Speed',
        'Lat°', 'House'
    ]
    p=sp.read_stdout(
        cmd=' '.join(
            binary + common_args + birth_args + config_args + 
            house_args + format_args
        ), 
        reader='table', sep='\s+', col_names=colnames
    )
    # Replace 'Node' with Rahu & Ascendant with Lagna
    p.loc[
        p['Graha'].isin([
            'mean_Node', 'true_Node', 'Ascendant'
        ]), 'Graha'
    ] = ['Rahu (mean)', 'Rahu (true)', 'Lagna']
    # Add rows corresponding to Ketu
    p=add_ketu(p)    
    # Reorder rows sensibly
    p=reorder_swetest_rows(p)
    # Replace total degrees by degrees in house/sign
    p['Lon°']=p['Lon°'].str.replace(
        pat=r'^\d+',
        repl=lambda m: str(int(m.group(0))%30),
        regex=True
    )
    # House calculation
    p=add_house(p)
    return p

def add_house(p):
    p['Sign']=p['Lon'].apply(lambda x: int(divmod(x, 30)[0]+1))
    lagna_rashi=p.loc[p['Graha']=='Lagna', 'Sign']
    p['Bhava']=p['Sign'].apply(lambda x: ((x+(12-lagna_rashi))%12)+1)
    return p

def reorder_swetest_rows(p):
    p['ix']=[
        2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 10, 9, 14, 15, 16, 17, 18, 
        19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 
        35, 1, 36, 37, 38, 39, 40, 41, 42, 10.5, 9.5
    ]
    p.set_index('ix', inplace=True)    
    p=p.sort_index()
    p=p.reset_index(drop=True)
    return p

def add_ketu(p):    
    # Select rows corresponding to Rahu
    ketu=p.loc[
        p['Graha'].isin(['Rahu (true)', 'Rahu (mean)'])
    ]
    # Convenience function to add 180° to dms
    def add_180_deg(x):
        x_deg=str((int(re.search(r'^\d+', x).group(0))+180)%360)
        x_min_sec='°'+re.search(r'(?<=°).*', x).group(0)        
        return x_deg+x_min_sec
    # Replace 'Rahu' with 'Ketu' and add 180°
    # House calculation not done here as can be done in one fell swoop
    ketu.loc[:, ['Graha', 'Lon', 'Lon°']]=pd.DataFrame({
        'Graha':ketu['Graha'].str.replace('Rahu', 'Ketu'), 
        'Lon':ketu['Lon'].apply(lambda x: (x+180)%360), 
        'Lon°':ketu['Lon°'].apply(add_180_deg)
    })
    p_out=pd.concat([p, ketu])
    # Reset index required because concatenate creates repeated indices
    p_out.reset_index(drop=True)
    return p_out

def add_non_equi_col(p1, p2, p1col, p2col_high, p2col_low, p2col_get):
    # Create column of p2's indices in p1 
    # that correspond to value between high and low
    matched_idx=p1[p1col].apply(
        lambda x: p2[(p2[p2col_low]<=x) & (x<p2[p2col_high])].index.item()
    )
    # Append columns from p2 corresponding to the indices
    # These columns may contain repeated rows, so reset index
    p1[p2col_get]=p2.iloc[
        matched_idx, p2.columns.get_indexer(p2col_get)
    ].reset_index(drop=True)
    return p1

def round_cols(p, cols, round):
    for col, rd in zip(cols, round):
        if pd.api.types.is_numeric_dtype(p[col]):
            p[col]=p[col].round(rd)
        elif pd.api.types.is_object_dtype(p[col]):
            p[col]=p[col].str.replace(
                r'(?<=\.).*', 
                # The commented lambda works in terminal, but not in function
                # lambda m: str(round(float(m.group(0)),rd)), 
                lambda m: m.group(0)[0:rd], 
                regex=True
            )
    return p

def birth_datetime_args(dt):    
    # Convert to UTC
    birth_datetime_utc=dt.astimezone(pytz.utc)
    # Create birthdate input for swetest
    birth_date='-b'+birth_datetime_utc.strftime('%d.%m.%Y')
    # Create birthtime input for swetest
    birth_time='-utc'+birth_datetime_utc.strftime('%H:%M.%S')
    return [birth_date, birth_time]

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
