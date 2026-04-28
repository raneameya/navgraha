from zoneinfo import ZoneInfo
from datetime import datetime
from functools import cached_property

from core.chart.chart_plot_constants import rasi_dict
from core.divisionals import (
    Rasi, Navamsa, Hora, Drekkana, Chathurtamsa, Saptamsa, Dasamsa,
    Dvadasamsa, Sodasamsa, Vimsamsa, Siddhamsa, Nakshatramsa, Trimsamsa,
    Khavedamsa, Aksavedamsa, Shashtiamsa
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
        dark: bool,
        style: str,
        rasis: dict = rasi_dict # dict map of house/sign num to unicode glyph
    ):
        '''
        Plots the chart. Strips the chart down to chart_minimal and plots it.
        Args:
            dark (bool): Set to true for dark mode friendly plotting
            style (str): Can be one of 'North Indian' or 'South Indian'
            rasis (dict): Leave unchanged. By default imports a dictionary
                        mapping rasi to unicode glyph of that rasi
        Returns:
            A matplot figure
        '''
        fig = self.rasi.chart_plot(dark = dark, style = style, rasis = rasis)
        return fig

class _divisionals:
    '''
    A class (in this instance, used as a namespace) to hold
    all divisional charts
    '''
    def __init__(self, parent_chart: chart):
        self.parent = parent_chart

    @cached_property
    def rasi(self):
        return Rasi.d1(self.parent)

    @cached_property
    def navamsa(self):
        return Navamsa.d9(self.parent)

    @cached_property
    def hora_psr(self):
        return Hora.d2(self.parent, type = 'Parashari')

    @cached_property
    def hora_us(self):
        return Hora.d2(self.parent, type = 'Uma Shambhu')

    @cached_property
    def hora_prv(self):
        return Hora.d2(self.parent, type = 'Parivṛtti')

    @cached_property
    def hora_ksn(self):
        return Hora.d2(self.parent, type = 'Kāśīnāth')

    @cached_property
    def hora_jgn(self):
        return Hora.d2(self.parent, type = 'Jagannāth')

    @cached_property
    def hora_ssp(self):
        return Hora.d2(self.parent, type = 'Samasaptaka')

    @cached_property
    def hora_mdk(self):
        return Hora.d2(self.parent, type = 'Maṇḍūka')

    @cached_property
    def hora_lmk(self):
        return Hora.d2(self.parent, type = 'Lābha maṇḍūka')

    @cached_property
    def drekkana_psr(self):
        return Drekkana.d3(self.parent, type = 'Parashari')

    @cached_property
    def drekkana_prv(self):
        return Drekkana.d3(self.parent, type = 'Parivṛtti')

    @cached_property
    def drekkana_jgn(self):
        return Drekkana.d3(self.parent, type = 'Jagannāth')

    @cached_property
    def drekkana_smn(self):
        return Drekkana.d3(self.parent, type = 'Somanāth')

    @cached_property
    def drekkana_us(self):
        return Drekkana.d3(self.parent, type = 'Uma Shambhu')

    @cached_property
    def chathurtamsa_psr(self):
        return Chathurtamsa.d4(self.parent, type = 'Parashari')

    @cached_property
    def chathurtamsa_prv(self):
        return Chathurtamsa.d4(self.parent, type = 'Parivṛtti')

    @cached_property
    def saptamsa_psr(self):
        return Saptamsa.d7(self.parent, type = 'Parashari')

    @cached_property
    def saptamsa_rev17(self):
        return Saptamsa.d7(self.parent, type = 'Parashari reversed (1-7)')

    @cached_property
    def saptamsa_rev71(self):
        return Saptamsa.d7(self.parent, type = 'Parashari reversed (7-1)')

    @cached_property
    def dasamsa_psr(self):
        return Dasamsa.d10(self.parent, type = 'Parashari')

    @cached_property
    def dasamsa_rev(self):
        return Dasamsa.d10(self.parent, type = 'Parashari reversed')

    @cached_property
    def dasamsa_rev69(self):
        return Dasamsa.d10(self.parent, type = 'Parashari reversed (6-9)')

    @cached_property
    def dvadasamsa_psr(self):
        return Dvadasamsa.d12(self.parent, type = 'Parashari')

    @cached_property
    def dvadasamsa_rev(self):
        return Dvadasamsa.d12(self.parent, type = 'Parashari reversed')

    @cached_property
    def sodasamsa_psr(self):
        return Sodasamsa.d16(self.parent, type = 'Parashari')

    @cached_property
    def sodasamsa_rev(self):
        return Sodasamsa.d16(self.parent, type = 'Parashari reversed')

    @cached_property
    def vimsamsa_psr(self):
        return Vimsamsa.d20(self.parent, type = 'Parashari')

    @cached_property
    def vimsamsa_rev(self):
        return Vimsamsa.d20(self.parent, type = 'Parashari reversed')

    @cached_property
    def siddhamsa_psr(self):
        return Siddhamsa.d24(self.parent, type = 'Parashari')

    @cached_property
    def siddhamsa_rev(self):
        return Siddhamsa.d24(self.parent, type = 'Parashari reversed')

    @cached_property
    def naksatramsa_psr(self):
        return Nakshatramsa.d27(self.parent, type = 'Parashari')

    @cached_property
    def naksatramsa_rev(self):
        return Nakshatramsa.d27(self.parent, type = 'Parashari reversed')

    @cached_property
    def trimsamsa_psr(self):
        return Trimsamsa.d30(self.parent, type = 'Parashari')

    @cached_property
    def trimsamsa_prv(self):
        return Trimsamsa.d30(self.parent, type = 'Parivṛtti')

    @cached_property
    def khavedamsa(self):
        return Khavedamsa.d40(self.parent)

    @cached_property
    def aksavedamsa(self):
        return Aksavedamsa.d45(self.parent)

    @cached_property
    def sastyamsa_psr(self):
        return Shashtiamsa.d60(self.parent, type = 'Parashari')

    @cached_property
    def sastyamsa_rev(self):
        return Shashtiamsa.d60(self.parent, type = 'Parashari reversed')
