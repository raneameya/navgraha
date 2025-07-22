
# Measure time performance of two different non-equi joins
import chart as crt
import misc_functions as mf
import pandas as pd
from constants import rnp

cc = crt.chart(
    b_yr = 1991,
    b_mo = 6,
    b_da = 15,
    b_hr = 8, 
    b_mi = 41, 
    b_sc = 0, 
    b_lon = 77.197, 
    b_lat = 28.48728, 
    b_tz = 'Asia/Kolkata', 
    ay = '-sid29'
)
input_df = pd.DataFrame.copy(
    cc.placement_compute()[['Date', 'Time', 'Graha', 'Lon', 'Speed']]
)
for i in range(1000):
    mf.add_non_equi_col(
        p1 = input_df, p2 = rnp, p1col = 'Lon', p2col_range = 'Degrees', 
        p2col_get = ['Rashi', 'Nakshatra', 'Nakshatra lord', 'Pada']
    )
