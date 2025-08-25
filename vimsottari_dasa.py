import chart as crt # chart class used as input
import numpy as np # cumsum
import pandas as pd # dataframe, interval
from constants import rnp, nakshatra # lookup table to provide to class
from misc_functions import cyclic_shift
import datetime as dt # timedeltas used
from fractions import Fraction as fr

class vimsottari_dasa:
    '''
    A class that computes and stores information about the vimsottari daśā
    for a given chart.
    The sub_dasa attributes are a list of dasa_intervals depending on sub_dasa_level
    Args:
        chart (chart): The natal chart for which the daśās need to be computed.
        seed_graha (str): This is usually Moon, unless some other graha is extremely powerful in the chart or the Moon is exceptionally weak.
        sub_dasa_level (int): One of the following 0:'Mahadaśā', 1:'Antardaśā', 2:'Pratyantardaśā', 3:'Sookshmaantardaśā', 4:'Praanaantardaśā', 5:'Dehaantardaśā'
        dasa_offset_days (int): By how many days should all the daśā periods be shifted in the future?
        trunc_intervals (bool): Should the dasa (or sub-dasa) periods be truncated to days? Set False to see more precise daśā intervals.
        yr_len (float): How long should a year be?
        lifespan (int): How long should the entire dasa period be? Default is 120 years for a natal chart, but can be changed for other use cases like tājaka.
        rnp_lut (DataFrame): rasi, nakshatra, pada lookup table. Leave unchanged.
    Returns:
        vimsottari_dasa: A vimsottari_dasa object with various attributes
    Attributes:
        dasa_names (list[str]): A list of the names of the 6 sub-dasa levels. Provided for convenience and reuse
        nakshatra (str): The nakshatra in which the seed graha lies
        nakshatra_lord (str): The graha lord of the nakshatra in which the seed graha lies
        dasa_covered (float): A fraction in [0, 1) indicating how much of the nakshatra has the seed graha covered. This determines when the daśā starts. A larger fraction means that the daśā of nakshatra lord began more in the past relative to the natal birth.
        dasas (DataFrame): A DataFrama with 9^(`sub_dasa_level` + 1) rows. Each row corresponds to 1. a tuple of grahas as period lords and sub-lords, and 2. the start & end time for that dasa period.
    Methods:
        compute_sub_dasa_shares: Calculates the shares (sum to 1) of all subdasa periods based on the requested `sub_dasa_level`. These shares can be scaled up to the lifespan interval to get the actual dasa intervals.
        dasa_to_df: Exists only for compatibility with old implementation.
    '''
    def __init__(
        self,
        chart:crt.chart,
        seed_graha:str = 'Moon',
        sub_dasa_level:int = 0,
        dasa_offset_days:int = 0,
        trunc_intervals:bool = False,
        yr_len:float = 365.25,
        lifespan:int = 120,
        rnp_lut: pd.DataFrame = rnp
    ):
        self.chart = chart
        self.seed = seed_graha
        self.sub_dasa_level = sub_dasa_level + 1
        self.dasa_offset_days = dasa_offset_days
        self.trunc_intervals = trunc_intervals
        self.dasa_names = [
            'Mahadaśā', 'Antardaśā', 'Pratyantardaśā', 'Sookshmaantardaśā',
            'Praanaantardaśā', 'Dehaantardaśā'
        ]
        chart_df = chart.placements
        # Longitude of the seed graha
        seed_deg = chart_df.loc[
            chart_df['Graha'] == seed_graha, 'Lon'
        ].squeeze()
        # At the longitude of the seed graha, how much of an interval
        # (in this case pada, i.e. a 3° 20' interval) has the graha covered?
        rnp_lut['Dasa covered'] = rnp_lut['Degrees'].apply(
            lambda x: x.point_in_range_coverage(seed_deg)
        )
        # Identify the interval the seed graha is in
        rnp_lut['Is in'] = rnp_lut['Degrees'].apply(
            lambda x: x.isin(seed_deg)
        )
        # Sorting by categorical nakshatra is important because this
        # allows meaningful sequential subsets
        rnp_gb = rnp_lut.groupby(
            ['Nakshatra', 'Nakshatra lord'], observed = True, sort = True
        ).agg(
            Dasa_covered = ('Dasa covered', 'mean'),
            IsIn = ('Is in', 'mean'), 
            Lord = ('Nakshatra lord', 'min'), # i.e. pick one as all are same
            Length = ('Vimshottari dasa (yrs)', 'sum')
        )
        # Which nakshatra does the seed graha lie in,
        # and who is that nakshatra's lord?
        self.nakshatra, self.nakshatra_lord = rnp_gb[
            rnp_gb['IsIn'] > 0
        ].index.values[0]
        # What is the length of the mahadasa of the nakshatra lord?
        nakshatra_lord_mahadasa_len = rnp_gb.at[
            (self.nakshatra, self.nakshatra_lord), 'Length'
        ].squeeze()
        # Scale mahadasa length as per lifespan
        nakshatra_lord_mahadasa_len *= lifespan / 120
        # How much of the dasa is completed at the time of birth?
        self.dasa_covered = rnp_gb[rnp_gb['IsIn'] > 0][
            'Dasa_covered'
        ].squeeze()
        # Start datetime of lifespan, accounting for offset if any
        first_dasa_start = pd.Timestamp(chart.datetime) - (self.dasa_covered *
            dt.timedelta(
                days = nakshatra_lord_mahadasa_len * yr_len
            )
        ) + dt.timedelta(days = dasa_offset_days)
        dasa_lengths = {
            'Ketu': fr(7, 120), 'Venus': fr(20, 120), 'Sun': fr(6, 120), 
            'Moon': fr(10, 120), 'Mars': fr(7, 120), 'Rahu': fr(18, 120), 
            'Jupiter': fr(16, 120), 'Saturn': fr(19, 120), 
            'Mercury': fr(17, 120)
        }
        sub_dasa_shares = self.compute_sub_dasa_shares(
            dasa_length_dict = dasa_lengths,
            sub_level = sub_dasa_level + 1, 
            start_lord = self.nakshatra_lord
        )
        sub_dasa_datetimes = [first_dasa_start] + [
            first_dasa_start + dt.timedelta(days = delta * yr_len * lifespan)
            for delta in sub_dasa_shares['Length'].to_list()
        ]
        sub_dasa_shares['Period'] = [
            pd.Interval(
                left = sub_dasa_datetimes[i], 
                right = sub_dasa_datetimes[i + 1],
                closed = 'left'
            )
            for i in range((len(sub_dasa_datetimes) - 1))
        ]
        sub_dasa_shares.drop(labels = 'Length', axis = 1, inplace = True)
        sub_dasa_shares['Length'] = sub_dasa_shares['Period'].apply(
            lambda x: (x.right - x.left)
        )
        if trunc_intervals:
            sub_dasa_shares['Period'] = sub_dasa_shares['Period'].apply(
                func = lambda x: (
                    # 'closed' attribute of interval is ignored
                    # Use "" because '' are used inside fstring
                    f"{x.left.strftime('%d-%m-%Y')} - "
                    f"{x.right.strftime('%d-%m-%Y')}"
                )
            )
        self.dasas = sub_dasa_shares

    def compute_sub_dasa_shares(
        self, 
        dasa_length_dict:dict,
        sub_level:int,
        start_lord:str
    ):
        lords = list(dasa_length_dict.keys())
        # cyclic shift `dasa_length_dict` to make start_lord as the first key-value pair
        dasa_length_dict = {
            k: dasa_length_dict[k] for k in cyclic_shift(
                x = lords, start = lords.index(start_lord)
            )
        }
        def calculate_dasa_length(d, rp, dl = dasa_length_dict):
            '''
            Recursive function to calculate share of dasas from the 
            dictionary of {graha:share of total dasa} pairs by tupling the 
            keys in a cartesian product and using regular math product for 
            the shares.
            '''
            if rp == 0: return d
            dl_keys = list(dasa_length_dict.keys())
            # For the next sub-level call the function with dl cyclic shifted 
            # so that the start lord is the same as the lord of k1 
            # (i.e. previous dasa lord), unless k1 is the lifespan and 
            # has no lord
            return calculate_dasa_length(
                d = {
                    k1+(k2,): d[k1]*dl[k2] 
                    for k1 in d 
                    for k2 in ({
                        k:dl[k] for k in cyclic_shift(
                            x = dl_keys, 
                            start = dl_keys.index(k1[(len(k1)-1)])
                        )
                    } if len(k1) > 0 else dl)
                },
                rp = rp - 1
            )
        # `{():1}` is the neutral element of the dasa_length_dict on which 
        # the shares can be built
        out = calculate_dasa_length({():1}, rp = sub_level)
        dasa_shares = pd.DataFrame(
            data = list(out.keys()), columns = self.dasa_names[0:sub_level]
        )
        dasa_shares['Length'] = np.cumsum(list(out.values()))
        return dasa_shares

    def dasa_to_df(self):
        '''
        Exists only for compatibility with the older implementation of 
        vimsottari_dasa which had a dasa_to_df method
        '''
        return self.dasas
