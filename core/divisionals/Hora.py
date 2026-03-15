import core.misc.misc_functions as mf
import core.chart.chart as crt
from core.chart.chart_minimal import chart_minimal
from core.data.constants import rasis, rnp
from core.divisionals.divisional_helpers import add_house

amsa_devata_mapping = {
    1: 'Devās - Sun', 2: 'Pitṛs - Moon'
}
amsa_devata_mapping_rev = {
    1: 'Pitṛs - Moon', 2: 'Devās - Sun'
}

def d2(birth_crt:crt.chart) -> chart_minimal:
    '''
    Compute the hora (D-2) of a birth chart
    Args:
        birth_crt (chart): The natal (D-1) chart for which the hora need to be computed.
    Returns:
        A chart_minimal object with the hora placements including degrees
    '''
    p = birth_crt.rasi.placements.copy(deep = True)
    # Create a copy of sign in rasi
    p['Rasi sign'] = p['Sign']
    # Which amsa is a planet in? (i.e. 0-1)
    p['Amsā'] = p['Lon30'].apply(lambda x: int(x // (30/2)))
    # Maping of hora indices (0-23) to sign in hora
    horaindex_horasign_mapping = [
        n for i in range(1, 12, 4) for n in (i, i + 1, i + 3, i + 2)
    ] * 2
    # Find out hora index (0-23) based on the sign and the half of the sign 
    # in which the graha is
    p['Hora index'] = p.apply(
        lambda df: (df['Sign'] - 1) * 2 + df['Amsā'], axis = 1
    )
    p['Sign'] = p['Hora index'].apply(lambda x: horaindex_horasign_mapping[x])
    # Pull in info about amsā devata
    p['Amsā Devatā'] = p.apply(
        lambda df: (
            amsa_devata_mapping[df['Amsā'] + 1] if df['Rasi sign'] % 2 != 0
            else amsa_devata_mapping_rev[df['Amsā'] + 1]
        ), axis = 1
    )
    # How much has the planet progressed in the amsā?
    p['Lon30'] = p.apply(lambda df: (
            30 * ((df['Lon30']/(30/2))%1) if df['Rasi sign'] % 2 != 0
            else 30 - (30 * ((df['Lon30']/(30/2))%1))
        ), axis = 1
    )
    p['Rashi'] = p['Sign'].apply(lambda x: list(rasis['Rasi'])[x - 1])
    p['Lon°'] = p['Lon30'].apply(lambda x: mf.dms(degrees = x))
    p['Lon'] = p.apply(lambda x: x['Lon30'] + 30 * x['Sign'] - 30, axis = 1)
    p = add_house(p = p)
    add_cols = ['Rashi', 'Nakshatra', 'Nakshatra lord', 'Pada']
    p = mf.add_non_equi_col(
        p1 = p,
        p2 = rnp,
        p1col = 'Lon',
        p2col_range = 'Degrees',
        p2col_get = add_cols
    )
    p = p[[
        'Date', 'Time', 'tz', 'Graha', 'Lon', 'Lon°', 'Lon30', 'Amsā', 
        'Amsā Devatā', 'Sign', 'Bhava', 'Rashi', 'Nakshatra', 
        'Nakshatra lord', 'Pada', 'Speed'
    ]]
    out = chart_minimal(
        placements = p, 
        display_cols = [
            'Graha', 'Lon°', 'Amsā Devatā', 'Nakshatra', 
            'Nakshatra lord', 'Pada'
        ]
    )
    return out
