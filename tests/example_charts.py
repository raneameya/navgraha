from datetime import datetime
from zoneinfo import ZoneInfo
from core.chart.chart import chart
from core.misc.birth_event import BirthEvent
from core.sweadaptor.swisseph_adaptor import SwissEphAdaptor

# 5 planet stellium in 5H
example_chart1 = chart(
    swisseph_adaptor = SwissEphAdaptor(
        base_path = './swisseph-master/',
        binary = 'swetest', 
        birth_event = BirthEvent(
            dt = datetime(2021, 2, 9, 22, 22, 0, tzinfo = ZoneInfo('Pacific/Auckland')), 
            latitude = -36.85582, longitude = 174.74304, z_height = 0, 
            place = 'Auckland'
        ),
        ayanamsa = 'True Pushya (PVRN Rao)',
        house = 'W',
        output_cols = 'TPlLsBj',
        ephemeris_path = 'ephe'
    )
)
# 6 planet (+ BB) stellium in 6H
example_chart2 = chart(
    swisseph_adaptor = SwissEphAdaptor(
        base_path = './swisseph-master/',
        binary = 'swetest', 
        birth_event = BirthEvent(
            dt = datetime(2025, 3, 29, 20, 22, 0, tzinfo = ZoneInfo('Pacific/Auckland')), 
            latitude = -36.85582, longitude = 174.74304, z_height = 0, 
            place = 'Auckland'
        ),
        ayanamsa = 'True Pushya (PVRN Rao)',
        house = 'W',
        output_cols = 'TPlLsBj',
        ephemeris_path = 'ephe'
    )
)
# 7 planet stellium in lagna
example_chart3 = chart(
    swisseph_adaptor = SwissEphAdaptor(
        base_path = './swisseph-master/',
        binary = 'swetest', 
        birth_event = BirthEvent(
            dt = datetime(2000, 5, 4, 6, 45, 0, tzinfo = ZoneInfo('Pacific/Auckland')), 
            latitude = -36.85582, longitude = 174.74304, z_height = 0, 
            place = 'Auckland'
        ),
        ayanamsa = 'Tropical',
        house = 'W',
        output_cols = 'TPlLsBj',
        ephemeris_path = 'ephe'
    )
)
# 8 planet stellium in lagna
example_chart4 = chart(
    swisseph_adaptor = SwissEphAdaptor(
        base_path = './swisseph-master/',
        binary = 'swetest', 
        birth_event = BirthEvent(
            dt = datetime(1962, 2, 4, 5, 50, 0, tzinfo = ZoneInfo('America/Los_Angeles')), 
            latitude = 34.05223, longitude = -118.24368, z_height = 0, 
            place = 'Los Angeles'
        ),
        ayanamsa = 'True Pushya (PVRN Rao)',
        house = 'W',
        output_cols = 'TPlLsBj',
        ephemeris_path = 'ephe'
    )
)
# 8 planet stellium in 3H
example_chart5 = chart(
    swisseph_adaptor = SwissEphAdaptor(
        base_path = './swisseph-master/',
        binary = 'swetest', 
        birth_event = BirthEvent(
            dt = datetime(1962, 2, 4, 2, 50, 0, tzinfo = ZoneInfo('America/Los_Angeles')), 
            latitude = 34.05223, longitude = -118.24368, z_height = 0, 
            place = 'Los Angeles'
        ),
        ayanamsa = 'True Pushya (PVRN Rao)',
        house = 'W',
        output_cols = 'TPlLsBj',
        ephemeris_path = 'ephe'
    )
)
# 4 planet stellium in 5H
example_chart6 = chart(
    swisseph_adaptor = SwissEphAdaptor(
        base_path = './swisseph-master/',
        binary = 'swetest', 
        birth_event = BirthEvent(
            dt = datetime(2021, 2, 21, 22, 22, 0, tzinfo = ZoneInfo('Pacific/Auckland')), 
            latitude = -36.85582, longitude = 174.74304, z_height = 0, 
            place = 'Auckland'
        ),
        ayanamsa = 'Tropical',
        house = 'W',
        output_cols = 'TPlLsBj',
        ephemeris_path = 'ephe'
    )
)
# 6 planet stellium in 5H
example_chart7 = chart(
    swisseph_adaptor = SwissEphAdaptor(
        base_path = './swisseph-master/',
        binary = 'swetest', 
        birth_event = BirthEvent(
            dt = datetime(2000, 5, 4, 2, 45, 0, tzinfo = ZoneInfo('America/Los_Angeles')), 
            latitude = -36.85582, longitude = 174.74304, z_height = 0, 
            place = 'Auckland'
        ),
        ayanamsa = 'Tropical',
        house = 'W',
        output_cols = 'TPlLsBj',
        ephemeris_path = 'ephe'
    )
)
# 6 planet (+ BB) stellium in 5H
example_chart8 = chart(
    swisseph_adaptor = SwissEphAdaptor(
        base_path = './swisseph-master/',
        binary = 'swetest', 
        birth_event = BirthEvent(
            dt = datetime(2025, 3, 29, 2, 22, 0, tzinfo = ZoneInfo('America/Los_Angeles')), 
            latitude = -36.85582, longitude = 174.74304, z_height = 0, 
            place = 'Auckland'
        ),
        ayanamsa = 'True Pushya (PVRN Rao)',
        house = 'W',
        output_cols = 'TPlLsBj',
        ephemeris_path = 'ephe'
    )
)
# 4 planet stellium in 9H
example_chart9 = chart(
    swisseph_adaptor = SwissEphAdaptor(
        base_path = './swisseph-master/',
        binary = 'swetest', 
        birth_event = BirthEvent(
            dt = datetime(2021, 2, 19, 14, 22, 0, tzinfo = ZoneInfo('America/Los_Angeles')), 
            latitude = -36.85582, longitude = 174.74304, z_height = 0, 
            place = 'Auckland'
        ),
        ayanamsa = 'True Pushya (PVRN Rao)',
        house = 'W',
        output_cols = 'TPlLsBj',
        ephemeris_path = 'ephe'
    )
)
# 4 planet stellium in 12H
example_chart10 = chart(
    swisseph_adaptor = SwissEphAdaptor(
        base_path = './swisseph-master/',
        binary = 'swetest', 
        birth_event = BirthEvent(
            dt = datetime(2021, 2, 19, 10, 22, 0, tzinfo = ZoneInfo('America/Los_Angeles')), 
            latitude = -36.85582, longitude = 174.74304, z_height = 0, 
            place = 'Auckland'
        ),
        ayanamsa = 'True Pushya (PVRN Rao)',
        house = 'W',
        output_cols = 'TPlLsBj',
        ephemeris_path = 'ephe'
    )
)
# 4 planet stellium in 8H
example_chart11 = chart(
    swisseph_adaptor = SwissEphAdaptor(
        base_path = './swisseph-master/',
        binary = 'swetest', 
        birth_event = BirthEvent(
            dt = datetime(2021, 2, 18, 20, 22, 0, tzinfo = ZoneInfo('America/Los_Angeles')), 
            latitude = -36.85582, longitude = 174.74304, z_height = 0, 
            place = 'Auckland'
        ),
        ayanamsa = 'True Citra',
        house = 'W',
        output_cols = 'TPlLsBj',
        ephemeris_path = 'ephe'
    )
)
# 6 planet (+ BB) stellium in lagna
example_chart12 = chart(
    swisseph_adaptor = SwissEphAdaptor(
        base_path = './swisseph-master/',
        binary = 'swetest', 
        birth_event = BirthEvent(
            dt = datetime(2025, 3, 29, 8, 22, 0, tzinfo = ZoneInfo('Pacific/Auckland')), 
            latitude = -36.85582, longitude = 174.74304, z_height = 0, 
            place = 'Auckland'
        ),
        ayanamsa = 'True Pushya (PVRN Rao)',
        house = 'W',
        output_cols = 'TPlLsBj',
        ephemeris_path = 'ephe'
    )
)
