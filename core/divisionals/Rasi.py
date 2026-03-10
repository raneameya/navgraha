from core.misc.misc_functions import add_non_equi_col
import core.chart.chart as crt
from core.chart.chart_minimal import chart_minimal
import core.misc.stdout_to_pd as sp
import pandas as pd
import re
from datetime import datetime
from core.data.constants import rasis, rnp
from core.divisionals.divisional_helpers import add_house
from core.sweadaptor.swisseph_reader import SwissEphReader

def d1(birth_crt: crt.chart) -> chart_minimal:
    p = swetest(adapter = birth_crt.swisseph_adaptor)
    # Keep classical planets (including Rahu, Ketu)
    p = p.head(10)
    # Add other details
    add_cols = ['Rashi', 'Nakshatra', 'Nakshatra lord', 'Pada', 'Pushkara']
    p = add_non_equi_col(
        p1 = p,
        p2 = rnp,
        p1col = 'Lon',
        p2col_range = 'Degrees',
        p2col_get = add_cols
    )
    # Reorder columns
    p = p[[
        'Date', 'Time', 'tz', 'Graha', 'Lon', 'Lon°', 'Lon30', 
        'Speed', 'Lat°', 'House', 'Sign', 'Bhava', 'Rashi', 
        'Nakshatra', 'Nakshatra lord', 'Pada', 'Pushkara'
    ]]
    return chart_minimal(
        placements = p, 
        display_cols = [
            'Graha', 'Lon°', 'Nakshatra', 'Nakshatra lord', 
            'Pada', 'Pushkara', 'Speed'
        ]
    )

def swetest(adapter: SwissEphAdaptor):
    p = SwissEphReader(
        se = adapter, 
        post_process = ' '.join([
            '| sed -E \'s/(UT\\s\\S+)(\\s{1,2})(\\w)/\\1_\\3/g\'',
            '| sed -E \'s/° /°/g\'', '| sed -E "s/\' /\'/g\"'
        ])
    ).planetary_positions()
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
    p['Lon°'] = p['Lon°'].str.replace(
        pat = r'^\d+',
        repl = lambda m: str(int(m.group(0))%30),
        regex = True
    )
    # House calculation
    p = add_house(p)
    # Add degrees in house as a numeric
    p['Lon30'] = p['Lon'].apply(lambda x: x%30)
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
