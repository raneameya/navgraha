from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from subprocess import run
from io import StringIO
import re
import pandas as pd
from core.misc.birth_event import BirthEvent
from core.sweadaptor.swisseph_adaptor import SwissEphAdaptor
import core.misc.stdout_to_pd as sp

@dataclass
class SwissEphReader:
    se: SwissEphAdaptor

    @staticmethod
    def str_to_date(datetime_str, tzi):
        formats = ['%d.%m.%Y %H:%M:%S.%f', '%d.%m.%Y %H:%M:%S']
        for fmt in formats:
            try:
                # Attempt to parse the string using the current format
                dt = datetime.strptime(datetime_str, fmt)
            except ValueError:
                # If parsing fails, continue to the next format
                continue
        dt = dt.replace(
            tzinfo = ZoneInfo('UTC')
        ).astimezone(
            tz = tzi
        )
        return dt

    def planetary_positions(self):
        bin_call = f'{self.se.base_path}{self.se.binary}'
        args = (
            self.se.ephemeris_path_arg |
            self.se.birth_moment_args() | 
            self.se.birth_place_args() | 
            self.se.ayanamsa_arg() |
            self.se.planet_args(planet_type = 'poi') |
            self.se.no_header_arg() | 
            self.se.output_cols_arg()
        )
        args = [bin_call] + [v for k, v in args.items() if v]
        colnames = [
            'Date', 'Time', 'tz', 'Graha', 'Lon', 'Lon°', 'Speed',
            'Lat°', 'House'
        ]
        p = sp.read_stdout(
            cmd = args, reader = 'fixed_width', sep = None, 
            col_names = colnames
        )
        return p

    def sun_rise_set(self):
        bin_call = f'{self.se.base_path}{self.se.binary}'
        # Need to offset the birth date because swetest does not show the 
        # rise time for the day of birth.
        args = (
            self.se.ephemeris_path_arg |
            self.se.birth_place_args() |
            self.se.birth_moment_args(offset_days = -3) | 
            self.se.no_header_arg() | 
            self.se.num_row_arg() |
            {
                'sunrise_flag': '-rise', 
                'sunrise_definition': '-hindu'
            }
        )
        args_needed = [
            'ephemeris_path', 'birth_date', 'geopos', 'no_header_info', 
            'num_rows', 'sunrise_flag', 'sunrise_definition'
        ]
        args = [bin_call] + [args[k] for k in args_needed if args[k]]
        colnames = [
            'Rise', 'Date-1', 'Rise time', 'Set', 'Date', 
            'Set time', 'DT', 'Equal sign', 'Day length'
        ]
        out = sp.read_stdout(
            cmd = args, reader = 'fixed_width', sep = None, 
            col_names = colnames
        )
        out = out.iloc[1:, [4, 2, 5]]
        out['Rise time'] = out.apply(
            lambda df: df['Date'] + ' ' + df['Rise time'], axis = 1
        ).apply(
            lambda x: self.str_to_date(x, self.se.birth_event.dt.tzinfo)
        )
        out['Set time'] = out.apply(
            lambda df: df['Date'] + ' ' + df['Set time'], axis = 1
        ).apply(
            lambda x: self.str_to_date(x, self.se.birth_event.dt.tzinfo)
        )
        # Adjust set time as the output is a quirk of swetest
        out['Set time'] = out.apply(
            lambda df: (
                df['Set time'] + timedelta(days = 1) 
                if df['Set time'] < df['Rise time'] 
                else df['Set time']
            ), axis = 1
        )
        out1 = out.copy()
        birth_datetime = self.se.birth_event.dt
        # First row where birth_datetime <= set_time contains rise and set 
        # times on that day. Next row is required for the sunrise of the next 
        # day indicating the end of the birthday.
        all_rise_times = out['Rise time'].to_list()
        all_set_times = out['Set time'].to_list()
        rise_time_idx = max([
            i for i, x in enumerate(all_rise_times) 
            if x <= birth_datetime
        ])
        rise_time = all_rise_times[rise_time_idx]
        set_time = all_set_times[rise_time_idx]
        rise_time_next_day = all_rise_times[rise_time_idx + 1]
        return (rise_time, set_time, rise_time_next_day)

    def graha1_graha2_rel_diff(self):
        bin_call = f'{self.se.base_path}{self.se.binary}'
        args = (
            self.se.ephemeris_path_arg |
            self.se.birth_moment_args() | 
            self.se.birth_place_args() | 
            self.se.planet_args(planet_type = 'poi') |
            self.se.planet_args(planet_type = 'pod') |
            self.se.num_row_arg() |
            self.se.time_delta_arg() |
            self.se.no_header_arg() | 
            self.se.output_cols_arg()
        )
        args_needed = [
            'ephemeris_path', 'birth_date', 'birth_time', 'geopos', 
            'no_header_info', 'planets_poi', 'planets_pod', 'num_rows', 
            'time_delta_arg', 'output_cols'
        ]
        args = [bin_call] + [args[k] for k in args_needed if args[k]]
        colnames = ['P1-P2', 'Date', 'Time', 'Timezone', 'Angular difference']
        p = sp.read_stdout(
            cmd = args, reader = 'table', sep = r'\s+', 
            col_names = colnames
        )
        p = p.iloc[:, [0, 1, 2, 4]]
        p['Datetime'] = p.apply(lambda df: self.str_to_date(
            datetime_str = df['Date'] + ' ' + df['Time'], 
            tzi = self.se.birth_event.dt.tzinfo
        ), axis = 1)
        return p[['P1-P2', 'Datetime', 'Angular difference']]
