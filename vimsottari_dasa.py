import chart as crt # chart class used as input
import numpy as np # cumsum
import pandas as pd # dataframe, interval
from constants import rnp, nakshatra # lookup table to provide to class
from misc_functions import cyclic_shift
import fractional_interval as fi # isin and pointinrange functions used
import datetime as dt # timedeltas used

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
        mahadasa (list[dasa_interval]): A list of 9 dasa_intervals, one for each graha.
        antardasa (list[dasa_interval]): If sub_dasa_level > 0, a list of 81 dasa_intervals, one for each pair of grahas.
        pratyantardasa (list[dasa_interval]): If sub_dasa_level > 1, a list of 729 dasa_intervals, one for each triple of grahas.
        sookshmaantardasa (list[dasa_interval]): If sub_dasa_level > 2, a list of 6561 dasa_intervals, one for each quadruple of grahas.
        praanaantardasa (list[dasa_interval]): If sub_dasa_level > 3, a list of 59049 dasa_intervals, one for each quintuple of grahas.
        dehaantardasa (list[dasa_interval]): If sub_dasa_level > 4, a list of 531441 dasa_intervals, one for each sextuple of grahas.
    '''
    def __init__(
        self,
        chart: crt.chart,
        seed_graha: str = 'Moon',
        sub_dasa_level:int = 0,
        dasa_offset_days:int = 0,
        trunc_intervals:bool = False,
        yr_len:float = 365.25,
        lifespan:int = 120,
        rnp_lut: pd.DataFrame = rnp
    ):
        self.chart = chart
        self.seed = seed_graha
        self.sub_dasa_level = sub_dasa_level
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
            lambda fi: fi.point_in_range_coverage(seed_deg)
        )
        # Identify the interval the seed graha is in
        rnp_lut['Is in'] = rnp_lut['Degrees'].apply(
            lambda fi: fi.isin(seed_deg)
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
        nakshatra_lord_mahadasa_len *= lifespan/120
        # How much of the dasa is completed at the time of birth?
        self.dasa_covered = rnp_gb[rnp_gb['IsIn'] > 0][
            'Dasa_covered'
        ].squeeze()
        # Start datetime of lifespan, accounting for offset days
        first_dasa_start = pd.Timestamp(chart.datetime) - (self.dasa_covered *
            dt.timedelta(days = nakshatra_lord_mahadasa_len * yr_len)
        ) + dt.timedelta(days = dasa_offset_days)
        # Create pandas.Interval corresponding to the lifespan
        lifespan_interval = pd.Interval(
            left = first_dasa_start,
            right = first_dasa_start + dt.timedelta(days = lifespan * yr_len),
            closed = 'left'
        )
        # Create dasa_interval object corresponding to the lifespan
        lifespan_di = dasa_interval(
            lord = None, interval = lifespan_interval, level = 0
        )
        # Compute mahadasas
        self.mahadasa = compute_sub_dasa(
            di = lifespan_di,
            first_mahadasa_lord = self.nakshatra_lord,
            yr_len = yr_len
        )
        if sub_dasa_level > 0:
            self.antardasa = [
                a for m in self.mahadasa
                for a in compute_sub_dasa(m, yr_len = yr_len)
            ]
        if sub_dasa_level > 1:
            self.pratyantardasa = [
                p for a in self.antardasa
                for p in compute_sub_dasa(a, yr_len = yr_len)
            ]
        if sub_dasa_level > 2:
            self.sookshmaantardasa = [
                s for p in self.pratyantardasa
                for s in compute_sub_dasa(p, yr_len = yr_len)
            ]
        if sub_dasa_level > 3:
            self.praanaantardasa = [
                p for s in self.sookshmaantardasa
                for p in compute_sub_dasa(s, yr_len = yr_len)
            ]
        if sub_dasa_level > 4:
            self.dehaantardasa = [
                d for p in self.praanaantardasa
                for d in compute_sub_dasa(p, yr_len = yr_len)
            ]

    def __str__(self):
        return f'Vimsottari dasha object for {self.chart.datetime}.'

    def dasa_to_df(self):
        level = self.sub_dasa_level
        cols = self.dasa_names
        if level == 0:
            di_list = self.mahadasa
        elif level == 1:
            di_list = self.antardasa
        elif level == 2:
            di_list = self.pratyantardasa
        elif level == 3:
            di_list = self.sookshmaantardasa
        elif level == 4:
            di_list = self.praanaantardasa
        elif level == 5:
            di_list = self.dehaantardasa
        # Create df from list of dasa_intervals
        df = pd.DataFrame(
            [
                [di.parent_lord, di.lord, di.interval, di.interval.length]
                for di in di_list
            ], columns = ['Parent lord(s)', 'Lord', 'Period', 'Length']
        )
        # TODO: Alternate approach, is there any performance difference?
        # df = pd.DataFrame({
        #     'Parent lord(s)': [di.parent_lord for di in di_list],
        #     'Lord': [di.lord for di in di_list],
        #     'Period': [di.interval for di in di_list],
        #     'Length': [di.interval.length for di in di_list]
        # })
        # Truncate interval columns for better readability
        if self.trunc_intervals:
            df['Period'] = df['Period'].apply(func = lambda x: (
                # 'closed' attribute of interval is ignored
                # Use "" because '' are used inside fstring
                f"{x.left.strftime('%d-%m-%Y')} - "
                f"{x.right.strftime('%d-%m-%Y')}"
            ))
        if level == 0:
            return df[
                ['Lord', 'Period', 'Length']
            ].rename(columns = {'Lord': 'Mahadaśā'})
        # Split tuple of parent lords to their own columns
        df[cols[0:level]] = df['Parent lord(s)'].apply(pd.Series)
        df.rename(columns = {'Lord': cols[level]}, inplace = True)
        # Reorder columns
        df = df[cols[0:(level + 1)] + ['Period', 'Length']]
        return df

class dasa_interval:
    '''
    Store information about dasa intervals. This class does NOT check 
    whether the input interval is a valid dasa
    '''
    def __init__(
        self,
        lord:str,
        interval:pd.Interval,
        level:int,
        parent_lord:tuple = None,
        yr_len:float = 365.25
    ):
        if (lord is None and level != 0):
            raise ValueError(f'''
                Level = {level} implies sub-dasa computation. So, a lord 
                must be specified. If you wish to compute mahadasas 
                (i.e. level = 0), then lord must be None.
            ''')
        if (lord is not None and level == 0):
            raise ValueError(f'''
                Level = 0 implies mahadasa computation. So, a lord must not 
                be specified. If you wish to define sub-dasas for {lord},
                then level must be > 0.
            ''')
        self.lord = lord
        self.interval = interval
        self.level = level
        self.parent_lord = parent_lord

    def __repr__(self):
        if self.level == 0:
            dasa_str = 'dasa'
            pl = ()
        else:
            pl = (self.lord) if self.parent_lord is None else self.parent_lord + (self.lord)
            dasa_str = 'sub-dasa'
        pl = [x for x in pl]
        return f'''{' '.join(pl)} {dasa_str}: {self.interval.left}-{self.interval.right}'''

def compute_sub_dasa(
    di:dasa_interval,
    yr_len:float,
    first_mahadasa_lord:str = None
):
    if di.level == 0 and first_mahadasa_lord is None:
        raise ValueError(f'''
            Mahadasa computation requires specifcation of the first mahadasa 
            lord. Please specify a graha as the first_mahadasa_lord.
        ''')
    if di.level != 0 and first_mahadasa_lord is not None:
        raise Warning(f'''
            Ignoring first_mahadasa_lord = {first_mahadasa_lord}, as subsequent 
            subdasas are inferred from the lordship of the input dasa.
            The first sub-lord will therefore be {di.lord}.
        ''')
    # Set first sub-dasa lord based on whether mahadasa or sub-dasa
    if di.lord is None:
        lord = first_mahadasa_lord # Maha
        parent_lord = [None for i in range(9)]
    else:
        lord = di.lord
    scale = di.interval.length / dt.timedelta(days = 120 * yr_len)
    # Create ordered list of sub-dasa lords and their lengths
    sub_lords = [
        'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 
        'Saturn', 'Mercury'
    ]
    sub_lengths = [scale * l for l in [7, 20, 6, 10, 7, 18, 16, 19, 17]]
    cyclic_shift_start_index = sub_lords.index(lord)
    sub_lords = cyclic_shift(
        x = sub_lords, start = cyclic_shift_start_index
    )
    sub_lengths = cyclic_shift(
        x = sub_lengths, start = cyclic_shift_start_index
    )
    # Helper array of timedeltas to add to sub_dasa_start_datetime
    sub_dasa_start_deltas = np.cumsum(np.array([
        dt.timedelta(days = yr_len * sl) for sl in sub_lengths
    ]))
    sub_dasa_start_datetime = di.interval.left
    # Create list of sub-dasa start datetimes
    sub_dasa_start_datetimes = [sub_dasa_start_datetime] + [
        sub_dasa_start_datetime + delta for delta in sub_dasa_start_deltas
    ]
    # Identify dasa hierarchy by parent lord 
    # Parent lords only exist for antardasa and below dasas
    if di.parent_lord is None:
        parent_lord = [(di.lord, ) for i in range(9)]
    else:
        parent_lord = [di.parent_lord + (di.lord, ) for i in range(9)]
    # Create datetime intervals of start and end times.
    # end of current dasa = start of next dasa
    sub_dasa_intervals = [
        dasa_interval(
            lord = sub_lords[i],
            interval = pd.Interval(
                left = sub_dasa_start_datetimes[i],
                right = sub_dasa_start_datetimes[i + 1],
                closed = 'left'
            ),
            level = di.level + 1,
            parent_lord = None if parent_lord[i][0] is None else parent_lord[i]
        )
        for i in range((len(sub_dasa_start_datetimes) - 1))
    ]
    return sub_dasa_intervals
