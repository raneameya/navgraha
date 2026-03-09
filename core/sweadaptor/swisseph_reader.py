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

    def planetary_positions(self):
        bin_call = f'{self.se.base_path}{self.se.binary}'
        args = (
            self.se.ephemeris_path_arg |
            self.se.birth_moment_args() | 
            self.se.birth_place_args() | 
            self.se.ayanamsa_arg() |
            self.se.planet_args() |
            self.se.misc_args() | 
            self.se.output_cols_arg()
        )
        post_process = ' '.join([
            '| sed -E \'s/(UT\\s\\S+)(\\s{1,2})(\\w)/\\1_\\3/g\'',
            '| sed -E \'s/° /°/g\'', '| sed -E "s/\' /\'/g\"'
        ])
        args = ' '.join([v for k, v in args.items()])
        final_call = bin_call + ' ' + args + post_process
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
        birth_offset = self.se.birth.dt - timedelta(days = 3)
        args = (
            self.se.ephemeris_path_arg |
            self.se.birth_place_args() | 
            self.se.misc_args() | 
            {
                'birth_date': f'-b{birth_offset:%d.%m.%Y}', 
                'num_days': f'-n{self.se.num_days}',
                'sunrise_flag': '-rise', 
                'sunrise_definition': '-hindu'
            }
        )
        args_needed = [
            'ephemeris_path', 'birth_date', 'geopos', 'no_header_info', 
            'num_days', 'sunrise_flag', 'sunrise_definition'
        ]
        args = {k: args[k] for k in args_needed}
        args = ' '.join([v for k, v in args.items()])
        post_process = ' | awk -v FS=\' \' \'{print $5, $3, $6}\''
        final_call = bin_call + ' ' + args + post_process
        cmd_run = run(
            final_call, capture_output = True, text = True, check = True, 
            shell = True
        )
        import csv
        from io import StringIO
        reader = csv.reader(StringIO(cmd_run.stdout), delimiter = ' ')
        def make_date(ldt):
            # ldt = list of date & times as [dt, rise_time, set_time] 
            # as provided by row of data
            rise_time = datetime.strptime(
                ' '.join(ldt[0:2]), '%d.%m.%Y %H:%M:%S.%f'
            ).replace(tzinfo = ZoneInfo('UTC')).astimezone(
                self.se.birth.dt.tzinfo
            )
            set_time = datetime.strptime(
                ' '.join([ldt[0], ldt[2]]), '%d.%m.%Y %H:%M:%S.%f'
            ).replace(tzinfo = ZoneInfo('UTC')).astimezone(
                self.se.birth.dt.tzinfo
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
