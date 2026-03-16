import datetime as dt # timedeltas used
from fractions import Fraction as fr

import numpy as np # cumsum
import pandas as pd # dataframe, interval

import core.chart.chart as crt # chart class used as input
from core.data.constants import rnp # lookup table to provide to class
from core.misc.misc_functions import cyclic_shift
from core.chart.chart_helpers import graha_nakshatra_traversal


class vimsottari_dasa:
    '''
    Computes and stores Vimsottari Daśā periods for a given chart. 
    
    This class calculates the Vimsottari Daśā timeline starting from a 
    specified seed graha (typically the Moon) and supports multiple 
    levels of sub-division (mahādaśā through dehāntardaśā). 
    
    The depth of subdivision is controlled by sub_dasa_level, and the 
    resulting daśā intervals are stored as a table with start and end times.

    Args:
        chart (chart): The natal chart for which the daśās need to be computed.
        seed_graha (str): This is usually the Moon, unless some other graha is 
            extremely powerful in the chart or the Moon is exceptionally weak.
        sub_dasa_level (int): Depth of daśā subdivision
            0:'Mahadaśā'
            1:'Antardaśā'
            2:'Pratyantardaśā'
            3:'Sookshmaantardaśā'
            4:'Praanaantardaśā'
            5:'Dehaantardaśā'
        dasa_offset_days (int): Number of days by which all daśā periods 
            are shifted into the future (or past if -ve).
        divisional (str): The divisional chart for which the daśā needs to 
            be computed. A full list of allowable inputs can be accessed at 
            TODO:...
        trunc_intervals (bool): Set False to retain higher precision daśā 
            intervals. True truncates the intervals to the days.
        yr_len (float): Approximately 365.25 for a year, but can make a 
            difference for dasas further into the future.
        lifespan (int): Total duration of the daśā cycle in years. Defaults 
            to 120 years for a natal chart, but some cases like tājaka need 1 
            year, and some entity charts use 144 years.
        rnp_lut (DataFrame): Rāśi-nakṣatra-pada lookup table. Typically 
            left unchanged.
    Attributes:
        dasa_names (list[str]): Names of the 6 sub-dasa levels, provided 
            for convenience.
        nakshatra (str): Nakṣatra in which the seed graha is located
        nakshatra_lord (str): Graha lord of the nakshatra in which the seed 
            graha is located
        nakshatra_traversed (float): A fraction in [0, 1) indicating how much 
            of the nakṣatra the seed graha has traversed at the time of birth. 
            This determines how far in the past the current mahādaśā began. 
            The remaining fraction determines the balance of the running 
            mahādaśā at birth.
        dasas (DataFrame): A DataFrama with 9^(`sub_dasa_level` + 1) rows. 
            Each row corresponds to:
            1. a tuple of grahas as period lords and sub-lords 
            2. the start & end time for that dasa period.
    Methods:
        compute_sub_dasa_shares: Calculates the shares (sum to 1) of all 
            subdasa periods based on the requested `sub_dasa_level`. 
            These shares can be scaled up to the lifespan interval to 
            get the actual dasa intervals.
        dasa_to_df: Exists for compatibility with old implementation.
    '''
    def __init__(
        self,
        chart: crt.chart,
        seed_graha: str = 'Moon',
        sub_dasa_level: int = 0,
        dasa_offset_days: int = 0,
        divisional: str = 'rasi', 
        trunc_intervals: bool = False,
        yr_len: float = 365.25,
        lifespan: int = 120,
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
        self.dasa_lengths = {
            'Ketu': fr(7, 120), 'Venus': fr(20, 120), 'Sun': fr(6, 120), 
            'Moon': fr(10, 120), 'Mars': fr(7, 120), 'Rahu': fr(18, 120), 
            'Jupiter': fr(16, 120), 'Saturn': fr(19, 120), 
            'Mercury': fr(17, 120)
        }
        chart_df = getattr(chart.divisionals, divisional).placements
        (
            self.nakshatra, self.nakshatra_lord, self.dasa_covered
        ) = graha_nakshatra_traversal(
            birth_chart = chart, graha = seed_graha, divisional = divisional
        )
        self.dasa_covered = 1 - self.dasa_covered
        # What is the length of the mahadasa of the nakshatra lord?
        nakshatra_lord_mahadasa_len = 120 * self.dasa_lengths[self.nakshatra_lord]
        # Scale mahadasa length as per lifespan
        nakshatra_lord_mahadasa_len *= lifespan / 120        
        # Start datetime of lifespan, accounting for offset if any
        first_dasa_start = (
            pd.Timestamp(chart.birth_event.dt) - 
            (self.dasa_covered *
                dt.timedelta(
                    days = nakshatra_lord_mahadasa_len * yr_len
                )
            ) + 
            dt.timedelta(days = dasa_offset_days)
        )
        sub_dasa_shares = self.compute_sub_dasa_shares(
            dasa_length_dict = self.dasa_lengths,
            sub_level = sub_dasa_level + 1, 
            first_mahadasa_lord = self.nakshatra_lord
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
        dasa_length_dict: dict,
        sub_level: int,
        first_mahadasa_lord: str
    ) -> pd.DataFrame:
        '''
        Compute a cumulative daśā timeline up to a specified sub-level.

        This method constructs all nested daśā periods (e.g. mahādaśā,
        antardaśā, pratyantara, etc.) up to `sub_level`, calculates their
        proportional durations using a recursive daśā length engine, and
        returns the result as a tabular timeline.

        The returned DataFrame lists each complete daśā sequence in order and
        provides the cumulative endpoint of each period, making it suitable
        for chronological mapping to actual dates.

        Args:
        dasa_length_dict (dict[tuple, float]): A mapping from daśā lords to 
            their proportional duration shares. The keys in this dictionary are 
            assumed to be the canonical daśā sequence and is used for cyclic 
            shifting.
        sub_level(int): The number of daśā levels to compute. For example:
            - 1 → mahādaśā only
            - 2 → mahādaśā + antardaśā
            - 3 → mahādaśā + antardaśā + pratyantaradaśā
        first_mahadasa_lord(str): The lord of the first mahādaśā

        Returns:
        pandas.DataFrame: A DataFrame with one row per complete daśā sequence. 
            Columns correspond to daśā levels (named according to 
            `self.dasa_names`), and the final column `Length` contains the 
            cumulative proportion of elapsed time for each period.
        '''
        lords = list(dasa_length_dict.keys())
        # cyclic shift `dasa_length_dict` to bring first_mahadasa_lord first
        dasa_length_dict = {
            k: dasa_length_dict[k] for k in cyclic_shift(
                x = lords, start = lords.index(first_mahadasa_lord)
            )
        }
        def calculate_dasa_length(
            period_shares: dict[tuple[str, ...], float], 
            sub_level: int, 
            dasa_shares: dict = dasa_length_dict
        ) -> dict[tuple[str, ...], float]:
            '''
            Recursively compute fraction of duration for nested daśā sequences.

            This function builds all possible daśā / sub-daśā paths up to a 
            given recursion depth (`sub_level`) and assigns each path a 
            proportional duration based on daśā length shares 
            (`dasa_length_dict`).

            Each recursion level subdivides the duration of its parent daśā 
            according to `dasa_length_dict`, with the constraint that 
            sub-periods are ordered cyclically starting from the lord of 
            the immediately preceding period.

            Args:            
            period_shares (dict[tuple, float]): A mapping from daśā paths 
                (represented as tuples of daśā lords) to their proportional 
                durations. The empty tuple ``()`` represents the root period 
                with total normalized duration 1.
            sub_level (int): Remaining recursion depth. Each decrement 
                corresponds to one additional sub-daśā level.
                (e.g. mahādaśā → antardaśā → pratyantaradaśā).
            dasa_shares (dict): A mapping from daśā lords to their 
                proportional duration shares.
            
            Returns:
            dict[tuple, float]: A dictionary mapping complete daśā paths 
            (tuples) to their proportional durations. The sum of all returned 
            values equals 1. 
            '''
            if sub_level == 0: return period_shares
            mahadasa_grahas = list(dasa_length_dict.keys())
            # For the next sub-level call the function with period_shares 
            # shifted cyclically with the start lord the same as the previous 
            # dasa lord. (unless period_shares is the lifespan and has no lord)
            return calculate_dasa_length(
                period_shares = {
                    parent_path+(next_lord,): (
                        period_shares[parent_path]*
                        dasa_shares[next_lord]
                    )
                    for parent_path in period_shares 
                    for next_lord in ({
                        lord:dasa_shares[lord] for lord in cyclic_shift(
                            x = mahadasa_grahas, 
                            start = mahadasa_grahas.index(
                                parent_path[(len(parent_path)-1)]
                            )
                        )
                    } if len(parent_path) > 0 else dasa_shares)
                },
                sub_level = sub_level - 1
            )
        # `{():1}` is the neutral element of the dasa_length_dict on which 
        # the shares can be built
        out = calculate_dasa_length({():1}, sub_level = sub_level)
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
