import pytz
import misc_functions as mf
from datetime import datetime
from constants import rnp
from chart_minimal import chart_minimal
from chart_plot_constants import rasi_dict
from functools import cached_property
from divisionals import Rasi

class chart:
    '''
    A class to create birth charts from input datetime, lat, lon & ayanamsa
    '''
    def __init__(
        self,
        b_yr:int,
        b_mo:int,
        b_da:int,
        b_hr:int,
        b_mi:int,
        b_sc:int,
        b_lon:float,
        b_lat:float,
        b_tz:str,
        ay:str,
        place:str = None
    ):
        self.lat = b_lat
        self.lon = b_lon
        self.ayanamsa = ay
        self.tz = b_tz
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
        self.repr_str = self.datetime.strftime('%d-%m-%Y %H:%M:%S %Z')
        self.divisionals = _divisionals(parent_chart = self)
        self.rasi = self.divisionals.rasi
        if place is not None:
            self.place = place
            self.repr_str = f'{self.repr_str} {place}({b_lat}, {b_lon})'

    def __repr__(self):
        return self.repr_str
    
    def chart_plot(
        self, 
        dark:bool, 
        style:str, 
        rasis:dict = rasi_dict # dict mapping house/sign number to unicode of that rasi
    ):
        '''
        Plots the chart. Strips the chart down to chart_minimal and plots it.
        Args:
            dark (bool): Set to true for dark mode friendly plotting
            style (str): Can be one of 'North Indian' or 'South Indian'
            rasis (dict): Leave unchanged. By default imports a dictionary mapping rasi to unicode glyph of that rasi
        Returns:
            A matplot figure
        '''
        crt = chart_minimal(placements = self.rasi)
        fig = crt.chart_plot(dark = dark, style = style, rasis = rasis)
        return fig

class _divisionals:
    '''
    A class (in this instance, used as a namespace) to hold all divisional charts
    '''
    def __init__(self, parent_chart:chart):
        self.parent = parent_chart
    
    @cached_property
    def rasi(self):
        out = Rasi.d1(self.parent)
        return out

def add_house(p):
    p['Sign'] = p['Lon'].apply(lambda x: int(divmod(x, 30)[0]+1))
    lagna_rashi = p.loc[p['Graha']=='Lagna', 'Sign']
    p['Bhava'] = p['Sign'].apply(lambda x: ((x+(12-lagna_rashi))%12)+1)
    return p
