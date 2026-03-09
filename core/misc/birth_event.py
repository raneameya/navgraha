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
