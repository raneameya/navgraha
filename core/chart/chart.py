from zoneinfo import ZoneInfo
from datetime import datetime
from functools import cached_property

from core.chart.chart_plot_constants import rasi_dict
from core.divisionals import (
    Rasi, Navamsa, Hora, Dasamsa, Shashtiamsa
)
from core.misc.birth_event import BirthEvent
from core.sweadaptor.swisseph_adaptor import SwissEphAdaptor
from core.sweadaptor.swisseph_reader import SwissEphReader

class chart:
    '''
    A class to create birth charts from input datetime, lat, lon & ayanamsa
    '''
    def __init__(
        self, 
        swisseph_adaptor: SwissEphAdaptor
    ):
        self.birth_event = swisseph_adaptor.birth_event
        self.swisseph_adaptor = swisseph_adaptor
        self.repr_str = (
            f'''{self.birth_event.dt.strftime('%d-%m-%Y %H:%M:%S %Z (%z)')}'''
            f' {self.birth_event.place} '
            f'{(self.birth_event.latitude, self.birth_event.longitude)}'
        )
        self.divisionals = _divisionals(parent_chart = self)
        self.rasi = self.divisionals.rasi

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
        fig = self.rasi.chart_plot(dark = dark, style = style, rasis = rasis)
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
    
    @cached_property
    def navamsa(self):
        return Navamsa.d9(self.parent)

    @cached_property
    def hora(self):
        return Hora.d2(self.parent)

    @cached_property
    def dasamsa_trd(self):
        return Dasamsa.d10(self.parent, type = 'Traditional Parashari')

    @cached_property
    def dasamsa_rev(self):
        return Dasamsa.d10(self.parent, type = 'Parashari reversed')

    @cached_property
    def dasamsa_rev69(self):
        return Dasamsa.d10(self.parent, type = 'Parashari reversed (6-9)')

    @cached_property
    def shashtiamsa_trd(self):
        return Shashtiamsa.d60(self.parent, type = 'Traditional Parashari')

    @cached_property
    def shashtiamsa_rev(self):
        return Shashtiamsa.d60(self.parent, type = 'Parashari reversed')
