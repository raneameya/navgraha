from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

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

    def __str__(self):
        print_str = (
          f'''{self.dt.strftime('%d-%m-%Y %H:%M:%S %Z (%z)')} '''
          f'{self.place} {(self.latitude, self.longitude)}'
        )
        return print_str
'''   
    def __repr__(self):
      repr_str = (
         f'BirthEvent(dt = {self.dt}, latitude = {self.latitude}, '
         f'longitude = {self.longitude}, z_height = {self.z_height}'
         f', place = {self.place})'
      )
'''