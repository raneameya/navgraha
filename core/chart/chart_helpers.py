from datetime import datetime

from core.chart.chart import chart
from core.data.constants import rnp # lookup table to provide to class
from core.sweadaptor.swisseph_reader import SwissEphReader

def graha_nakshatra_traversal(
    birth_chart: chart, 
    graha: str, 
    divisional: str
):
    chart_df = getattr(birth_chart.divisionals, divisional).placements
    # Longitude of the seed graha
    seed_deg = chart_df.loc[
        chart_df['Graha'] == graha, 'Lon'
    ].squeeze()
    # At the longitude of the seed graha, how much of an interval
    # (in this case pada, i.e. a 3° 20' interval) has the graha covered?
    rnp_lut = rnp.copy(deep = True)
    rnp_lut['Pada traversed'] = rnp_lut['Degrees'].apply(
        lambda x: x.point_in_range_coverage(seed_deg)
    )
    # Identify the interval the seed graha is in
    rnp_lut['Is in'] = rnp_lut['Degrees'].apply(
        lambda x: x.isin(seed_deg)
    )
    # Sorting by categorical nakshatra is important because this
    # allows meaningful sequential subsets
    rnp_gb = rnp_lut.groupby(
        ['Nakṣatra', 'Graha devatā'], observed = True, sort = True
    ).agg(
        Nakshatra_traversed = ('Pada traversed', 'mean'),
        IsIn = ('Is in', 'mean'), 
        Lord = ('Graha devatā', 'min'), # i.e. pick one as all are same
        Length = ('Viṃśottarī daśā length', 'sum')
    )
    # Identify the nakshatra the seed graha lie in, and its lord
    nakshatra, nakshatra_lord = rnp_gb[
        rnp_gb['IsIn'] > 0
    ].index.values[0]
    # How much of the nakshatra is traversed at the time of birth?
    nakshatra_traversed = rnp_gb[rnp_gb['IsIn'] > 0][
        'Nakshatra_traversed'
    ].squeeze()
    return (nakshatra, nakshatra_lord, 1 - nakshatra_traversed)

def sun_rise_set(birth_chart: chart) -> tuple[datetime, datetime, datetime]:
    return SwissEphReader(
        se = birth_chart.swisseph_adaptor
    ).sun_rise_set()
