import pytz, re, stdout_to_pd as sp, pandas as pd, misc_functions as mf
from datetime import datetime
from constants import rnp

class chart:
    """
    A class to create birth charts from input datetime, lat, lon & ayanamsa
    """
    def __init__(self, b_yr, b_mo, b_da, b_hr, b_mi, b_sc, b_lon, b_lat, b_tz, ay):
        self.lat = b_lat
        self.lon = b_lon        
        self.ayanamsa = ay
        # Create a datetime object in local timezone, from the individual 
        # inputs of year, month, date, hour, minute, second & timezone
        # Need to specify initial datetime without timezone
        dt = datetime(
            year = b_yr,
            month = b_mo,
            day = b_da,
            hour = b_hr,
            minute = b_mi,
            second = b_sc,
            tzinfo = None
        )
        # Create local timezone object
        local_tz = pytz.timezone(b_tz)
        # Then localise the initial timezoneless datetime object
        self.datetime = local_tz.localize(dt)    
    
    def compute_placements(self):
        # Avoid repititous compute if already computed once
        if hasattr(self, 'placements'):
            return self.placements
        else:
            # Get birthdate arguments in UTC for swetest
            birth_datetime_utc_args = birth_datetime_args(self.datetime)
            # location argument, assumed 0 z-height at birth
            location = '-geopos' + str(self.lon) + ',' + str(self.lat) + ',0'
            wd = './swisseph-master/'
            # User inputs expected: [UTC birth time, birth place, ayanamsa]
            input_args = birth_datetime_utc_args + [location] + [self.ayanamsa]
            p = swetest(sweedir = wd, birth_args = input_args)
            # Keep classical planets (including Rahu, Ketu)
            p = p.head(10)
            # Add other details
            add_cols = [
                'Rashi', 'Nakshatra', 'Nakshatra lord', 'Pada'                
            ]
            # p = mf.add_non_equi_col(
            #     p1 = p, 
            #     p2 = rnp,
            #     p1col = 'Lon',
            #     p2col_low = 'Start',
            #     p2col_high = 'End',
            #     p2col_get = add_cols
            # )
            p = mf.add_non_equi_col(
                p1 = p, 
                p2 = rnp,
                p1col = 'Lon',
                p2col_range = 'Degrees',
                p2col_get = add_cols
            )
            # Assign table to placements attribute
            self.placements = p
            return p


def birth_datetime_args(dt:datetime):    
    # Return a list of UTC birth date & UTC birth time 
    # from local birth datetime
    # Convert to UTC
    birth_datetime_utc = dt.astimezone(pytz.utc)
    # Create birthdate input for swetest
    birth_date = '-b'+birth_datetime_utc.strftime('%d.%m.%Y')
    # Create birthtime input for swetest
    birth_time = '-utc'+birth_datetime_utc.strftime('%H:%M:%S')
    return [birth_date, birth_time]

def swetest(sweedir, birth_args):
    # Point to where the ephemeris data files live
    edir = sweedir + 'ephe'
    # Binary to run, in this case swetest
    binary = [sweedir + 'swetest']
    # These arguments won't be exposed to the user 
    # (with the possible exception of planets)
    common_args = ['-pp', '-head', '-edir' + edir]    
    # Ayanamsa and output columns
    config_args = [birth_args[3], '-fTPlLsBj']
    # To get ascendant, we need to specify house system to swetest
    # House system defaults to whole sign
    house_args = [
        birth_args[2].replace('geopos', 'house').replace(',0', ',W')
    ]
    # Format output of swetest so that it is space delimited
    format_args = [
        '| sed -E \'s/(UT\\s\\S+)(\\s{1,2})(\\w)/\\1_\\3/g\'', 
        '| sed -E \'s/° /°/g\'', '| sed -E "s/\' /\'/g\"'
    ]
    colnames = [
        'Date', 'Time', 'tz', 'Graha', 'Lon', 'Lon°', 'Speed',
        'Lat°', 'House'
    ]
    p = sp.read_stdout(
        cmd = ' '.join(
            binary + common_args + birth_args + config_args + 
            house_args + format_args
        ), 
        reader = 'table', sep = '\s+', col_names = colnames
    )
    # Replace 'Node' with Rahu & Ascendant with Lagna
    p.loc[
        p['Graha'].isin([
            'mean_Node', 'true_Node', 'Ascendant'
        ]), 'Graha'
    ] = ['Rahu (mean)', 'Rahu (true)', 'Lagna']
    # Add rows corresponding to Ketu
    p = add_ketu(p)
    # Reorder rows sensibly
    p = reorder_swetest_rows(p)
    # Replace total degrees by degrees in house/sign
    p['Lon°']=p['Lon°'].str.replace(
        pat = r'^\d+',
        repl = lambda m: str(int(m.group(0))%30),
        regex = True
    )
    # House calculation
    p = add_house(p)
    return p

def reorder_swetest_rows(p):
    p['ix'] = [
        2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 10, 9, 14, 15, 16, 17, 18, 
        19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 
        35, 1, 36, 37, 38, 39, 40, 41, 42, 10.5, 9.5
    ]
    p.set_index('ix', inplace = True)
    p = p.sort_index()
    p = p.reset_index(drop = True)
    return p

def add_ketu(p):
    # Select rows corresponding to Rahu
    ketu = p.loc[
        p['Graha'].isin(['Rahu (true)', 'Rahu (mean)'])
    ]
    # Convenience function to add 180° to dms
    def add_180_deg(x):
        x_deg = str((int(re.search(r'^\d+', x).group(0))+180)%360)
        x_min_sec = '°'+re.search(r'(?<=°).*', x).group(0)        
        return x_deg + x_min_sec
    # Replace 'Rahu' with 'Ketu' and add 180°
    # House calculation not done here as can be done in one fell swoop
    ketu.loc[:, ['Graha', 'Lon', 'Lon°']] = pd.DataFrame({
        'Graha':ketu['Graha'].str.replace('Rahu', 'Ketu'), 
        'Lon':ketu['Lon'].apply(lambda x: (x+180)%360), 
        'Lon°':ketu['Lon°'].apply(add_180_deg)
    })
    p_out = pd.concat([p, ketu])
    # Reset index required because concatenate creates repeated indices
    p_out.reset_index(drop = True)
    return p_out

def add_house(p):
    p['Sign'] = p['Lon'].apply(lambda x: int(divmod(x, 30)[0]+1))
    lagna_rashi = p.loc[p['Graha']=='Lagna', 'Sign']
    p['Bhava'] = p['Sign'].apply(lambda x: ((x+(12-lagna_rashi))%12)+1)
    return p
