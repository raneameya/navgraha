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
    p
    return p