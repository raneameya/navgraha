import chart as crt # chart class used as input
import numpy as np # cumsum
import pandas as pd # dataframe & interval used
from constants import rnp # default value to provide to class
import fractional_interval as fi # isin and pointinrange functions used
import datetime as dt # timedeltas used

class vimsottari_dasa:
    '''
    A class that computes and stores information about the vimsottari dasa 
    for a given chart
    '''
    def __init__(
        self, 
        chart: crt.chart, 
        rnp_lut: pd.DataFrame = rnp, # rasi, nakshatra, pada lookup
        seed_graha: str = 'Moon', # usually moon, can be modified
        sub_dasa_level:int = 0,
        yr_len:float = 365.25
    ):
        self.chart = chart
        self.seed = seed_graha
        self.dasa_level = sub_dasa_level
        chart_df = chart.placements
        # What longitude is the seed graha at?
        seed_deg = chart_df.loc[chart_df['Graha'] == seed_graha, 'Lon'].squeeze()
        # At the longitude of the seed graha, how much of an interval 
        # (in this case pada, i.e. a 3° 20' interval) has the graha covered?
        rnp_lut['Dasa covered'] = rnp_lut['Degrees'].apply(
            lambda fi: fi.point_in_range_coverage(seed_deg)
        )
        # Identify the interval the seed graha is in
        rnp_lut['Is in'] = rnp_lut['Degrees'].apply(
            lambda fi: fi.isin(seed_deg)
        )
        rnp_gb = rnp_lut.groupby(
            ['Nakshatra', 'Nakshatra lord'], observed = True
        ).agg(
            Dasa_covered = ('Dasa covered', 'mean'),
            IsIn = ('Is in', 'mean')
        )
        # Only for test, delete next line
        self.rnp_gb = rnp_gb
        # Which nakshatra does the seed graha lie in, 
        # and who is that nakshatra's lord?
        self.nakshatra, self.nakshatra_lord = rnp_gb[
            rnp_gb['IsIn'] > 0
        ].index.values[0]
        # How much of the dasa is completed at the time of birth?
        self.dasa_covered = rnp_gb[rnp_gb['IsIn'] > 0][
            'Dasa_covered'
        ].squeeze()
        # Define the vimsottari dasa lords and their respective lengths
        lords = [
            'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 
            'Saturn', 'Mercury'
        ]
        lengths = [7, 20, 6, 10, 7, 18, 16, 19, 17]
        # Create dictionary with the first dasa as per nakshatra_lord 
        dasa_lengths = {
            lord: length for lord, length in zip(
                lords[lords.index(self.nakshatra_lord):] + lords[
                    0:lords.index(self.nakshatra_lord)
                ], 
                lengths[lords.index(self.nakshatra_lord):] + lengths[
                    0:lords.index(self.nakshatra_lord)
                ]
            )
        }
        # Compute the start datetime of the dasa of nakshatra_lord
        first_dasa_start = chart.datetime - (self.dasa_covered * dt.timedelta(
            days = dasa_lengths[self.nakshatra_lord] * yr_len
        ))
        # Helper array of timedeltas to add to first_dasa_start
        dasa_start_deltas = np.cumsum(np.array([
            dt.timedelta(yr_len * dasa_lengths[lord]) for lord in dasa_lengths
        ]))
        # Create list of dasa start datetimes
        dasa_start_datetimes = [first_dasa_start] + [
            first_dasa_start + delta for delta in dasa_start_deltas
        ]
        # Create datetime intervals of start and end times 
        # end of current dasa = start of next dasa
        dasa_intervals = [
            (dasa_start_datetimes[i], dasa_start_datetimes[i + 1]) 
            for i in range((len(dasa_start_datetimes) - 1))
        ]
        dasa_intervals = pd.arrays.IntervalArray.from_tuples(
            dasa_intervals, closed = 'left'
        )
        # Descriptive DataFrame containing info
        self.dasas = pd.DataFrame({
            'Lord': [lord for lord in dasa_lengths],
            'Period': dasa_intervals,
            'Length (days)': [(dasa_lengths[lord] * yr_len) for lord in dasa_lengths]
        })
    
    def __str__(self):
        return f'Vimsottari dasha object for {self.chart.datetime}.'
