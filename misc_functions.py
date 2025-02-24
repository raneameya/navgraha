from datetime import datetime
import pytz
import stdout_to_pd as sp

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
    # Point to where do the ephemeris data files live
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
    p=reorder_swetest_rows(p)
    p['Graha']=p['Graha'].str.replace('mean_Node', 'Rahu (mean)')
    p['Graha']=p['Graha'].str.replace('true_Node', 'Rahu (true)')
    p['Graha']=p['Graha'].str.replace('Ascendant', 'Lagna')
    return p

def reorder_swetest_rows(p):    
    p['ix']=[
        2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 10, 9, 14, 15, 16, 17, 18, 
        19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 
        35, 1, 36, 37, 38, 39, 40, 41, 42
    ]
    p.set_index('ix', inplace=True)    
    p=p.sort_index()
    p=p.rename_axis(None)
    return p