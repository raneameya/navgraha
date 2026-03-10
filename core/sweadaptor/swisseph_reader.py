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
    post_process: str = None

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
        args = ' '.join([v for k, v in args.items()])
        final_call = bin_call + ' ' + args + self.post_process
        colnames = [
            'Date', 'Time', 'tz', 'Graha', 'Lon', 'Lon°', 'Speed',
            'Lat°', 'House'
        ]
        p = sp.read_stdout(
            cmd = final_call, reader = 'table', sep = r'\s+', 
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
        args = {k: args[k] for k in args_needed}
        args = ' '.join([v for k, v in args.items()])
        # Does a cut version of this exists?
        post_process = (
            self.post_process or 
            ' | awk -v FS=\' \' \'{print $5, $3, $6}\''
        )
        final_call = bin_call + ' ' + args + post_process
        cmd_run = run(
            final_call, capture_output = True, text = True, check = True, 
            shell = True
        )
        import csv
        from io import StringIO
        reader = csv.reader(StringIO(cmd_run.stdout), delimiter = ' ')
        def str_to_date(datetime_str, tzi):
            dt = datetime.strptime(
                datetime_str, 
                '%d.%m.%Y %H:%M:%S.%f'
            ).replace(
                tzinfo = ZoneInfo('UTC')
            ).astimezone(
                tz = tzi
            )
            return dt
        def make_date(ldt):
            # ldt = list of date & times as [dt, rise_time, set_time] 
            # as provided by row of data
            rise_time = str_to_date(
                datetime_str = ' '.join(ldt[0:2]), 
                tzi = self.se.birth.dt.tzinfo
            )
            set_time = str_to_date(
                datetime_str = ' '.join([ldt[0], ldt[2]]), 
                tzi = self.se.birth.dt.tzinfo
            )
            if set_time < rise_time:
                set_time = set_time + timedelta(days = 1)
            return (rise_time, set_time)
        data = []
        for i, row in enumerate(reader):
            if i >= 2:
                rise_time, set_time = make_date(row)
                if rise_time <= self.se.birth.dt <= set_time:
                    return (rise_time, set_time)

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
        args = {k: args[k] for k in args_needed}
        post_process = self.post_process or '| cut -d\' \' -f1,2,3,6'
        args = ' '.join([v for k, v in args.items()])
        final_call = bin_call + ' ' + args + self.post_process
        colnames = ['P1-P2', 'Date', 'Time', 'Angular difference']
        p = sp.read_stdout(
            cmd = final_call, reader = 'table', sep = r'\s+', 
            col_names = colnames
        )
        return p
