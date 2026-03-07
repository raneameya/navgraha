from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

@dataclass
class BirthEvent:
    '''
    Container for a birth date and time with timezone awareness.

    The class serves two main purposes:
    1. Provides a structured representation of a birth timestamp
       including timezone information.
    2. Offers convenient conversion utilities for astrological
       calculations, including UTC conversion and generation of
       argument strings compatible with Swiss Ephemeris.

    This allows birth data to be defined once and reused across
    multiple calculations while ensuring consistent timezone handling.
    '''
    dt: datetime
    latitude: float
    longitude: float
    z_height: float
    place: str

    def utc_datetime(self):
        return self.dt.astimezone(ZoneInfo('UTC'))

@dataclass
class SwissEphAdapter:
    base_path: str
    binary: str
    birth: BirthEvent
    ayanamsa: str
    house: str
    output_cols: str
    ephemeris_path: str
    sed_substitutions: list[str]

    def __post_init__(self):
        # Point to where ephemeris files live. This isn't a 
        # function because it is univerally required in all calls
        self.ephemeris_path_arg = {
            'ephemeris_path': f'-edir{self.base_path}{self.ephemeris_path}'
        }

    def birth_moment_args(self) -> dict:
        utc = self.birth.utc_datetime()
        return {
            'birth_date': f'-b{utc:%d.%m.%Y}',
            'birth_time': f'-utc{utc:%H:%M:%S}'
        }

    def birth_place_args(self) -> dict:
        # lat lon
        ll = (
            f'{str(self.birth.longitude)},'
            f'{str(self.birth.latitude)},'
        )
        geopos_arg = f'-geopos{ll}{self.birth.z_height}'
        house_arg = f'-house{ll}{self.house}'
        return {
            'geopos': geopos_arg,
            'house': house_arg
        }

    def ayanamsa_arg(self):
        ayanamsas = {
            'Fagan/Bradley':'00',
            'Lahiri':'1',
            'De Luce':'2',
            'Raman':'3',
            'Usha/Shashi':'4',
            'Krishnamurti':'5',
            'Djwhal Khul':'6',
            'Yukteshwar':'7',
            'J.N. Bhasin':'8',
            'Babylonian/Kugler 1':'9',
            'Babylonian/Kugler 2':'10',
            'Babylonian/Kugler 3':'11',
            'Babylonian/Huber':'12',
            'Babylonian/Eta Piscium':'13',
            'Babylonian/Aldebaran = 15 Tau':'14',
            'Hipparchos':'15',
            'Sassanian':'16',
            'Galact. Center = 0 Sag':'17',
            'J2000':'18',
            'J1900':'19',
            'B1950':'20',
            'Suryasiddhanta':'21',
            'Suryasiddhanta (mean Sun)':'22',
            'Aryabhata':'23',
            'Aryabhata (mean Sun)':'24',
            'SS Revati':'25',
            'SS Citra':'26',
            'True Citra':'27',
            'True Revati':'28',
            'True Pushya (PVRN Rao)':'29',
            'Galactic (Gil Brand)':'30',
            'Galactic Equator (IAU1958)':'31',
            'Galactic Equator':'32',
            'Galactic Equator mid-Mula':'33',
            'Skydram (Mardyks)':'34',
            'True Mula (Chandra Hari)':'35',
            'Dhruva/Gal.Center/Mula (Wilhelm)':'36',
            'Aryabhata 522':'37',
            'Babylonian/Britton':'38',
            'Vedic/Sheoran':'39',
            'Cochrane (Gal.Center = 0 Cap)':'40',
            'Galactic Equator (Fiorenza)':'41',
            'Vettius Valens':'42',
            'Lahiri 1940':'43',
            'Lahiri VP285 (1980)':'44',
            'Krishnamurti VP291':'45',
            'Lahiri ICRC':'46',
            'Tropical':''
        }
        out = (
            '' if self.ayanamsa == 'Tropical' 
            else f'-sid{ayanamsas[self.ayanamsa]}'
        )
        return {'ayanamsa': out}

    def output_cols_arg(self):
        return {'output_cols': f'-f{self.output_cols}'}

    def misc_args(self):
        return {'no_header_info': '-head'}
    
    def planet_args(self):
        return {'planets': '-pp'}
    
    def call_str(self):
        bin_call = f'{self.base_path}{self.binary}'
        args = (
            self.ephemeris_path_arg |
            self.birth_moment_args() | 
            self.birth_place_args() | 
            self.ayanamsa_arg() |
            self.planet_args() |
            self.misc_args() | 
            self.output_cols_arg()
        )
        args = ' '.join([v for k, v in args.items()])
        final_call = bin_call + ' ' + args + self.sed_substitutions
        return final_call
