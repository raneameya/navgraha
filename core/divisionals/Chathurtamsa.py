# Caturthāṁśa
from core.misc.misc_functions import add_non_equi_col, dms
import core.chart.chart as crt
from core.chart.chart_minimal import chart_minimal
from core.data.constants import rasis, rnp
from core.divisionals.divisional_helpers import add_house

amsa_devata_mapping = {
    1: ('Sanaka', 'Deep focus in the pursuit of wealth and happiness'),
    2: ('Sanandana', 'Enjoy one\'s possessions without constant complaint'),
    3: ('Sanatkumāra', 'Youthful energy and courage to retain happiness despite changes'),
    4: ('Sanātana', 'Ability to regain happiness after a loss, indicating permanent or long-lasting stability.')
}

def d4(birth_chart, type: str) -> chart_minimal:
    '''
    Compute the caturthāṁśa (D-4) of a birth chart
    Args:
        birth_crt (chart): The base natal (D-1) chart.
    Returns:
        A chart_minimal object with the caturthāṁśa placements including degrees
    '''
    d = 4
    p = birth_chart.rasi.placements.copy(deep = True)
    # Create a copy of sign in rasi. Used to classify whether graha in 
    # even/odd sign
    p['Natal sign'] = p['Sign']
    # Which amsa is a planet in? (i.e. 0, 1, 2, 3)
    p['Amsā'] = p['Lon30'].apply(lambda x: int(x // (30 / d)))
    # Pull in info about amsā devata. Reverse pull if graha is in 
    # even sign natally
    p['Amsā Devatā'] = p.apply(
        lambda df: (
            amsa_devata_mapping[df['Amsā'] + 1][0]
            if df['Natal sign'] % 2 == 1
            else amsa_devata_mapping[d - df['Amsā']][0]
        ), 
        axis = 1
    )
    # How much has the planet progressed in the amsā?
    p['Lon30'] = p['Lon30'].apply(lambda x: 30*((x / (30 / d)) % 1))
    def d4_progression(natal_rasi: int, amsa: int, type: str) -> int:
        if type == 'Parashari':
            return ((natal_rasi - 1 + (amsa * 3)) % 12) + 1
        if type == 'Parivṛtti':
            start_rasi = (((natal_rasi - 1) % 3) * 4) + 1
            return start_rasi + amsa
    p['Sign'] = p.apply(
        lambda df: d4_progression(
            df['Natal sign'], df['Amsā'], type = type
        ), axis = 1
    )
    p['Rāśi'] = p['Sign'].apply(lambda x: list(rasis['Rāśi'])[x - 1])
    p['Lon°'] = p['Lon30'].apply(lambda x: dms(degrees = x))
    p['Lon'] = p.apply(lambda x: x['Lon30'] + 30 * (x['Sign'] - 1), axis = 1)
    p['Amsā'] = p['Amsā'].apply(lambda x: x + 1)
    p = add_house(p = p)
    add_cols = ['Rāśi', 'Nakṣatra', 'Graha devatā', 'Pada']
    p = add_non_equi_col(
        p1 = p,
        p2 = rnp,
        p1col = 'Lon',
        p2col_range = 'Degrees',
        p2col_get = add_cols
    )
    p = p[[
        'Birth', 'Graha', 'Lon', 'Lon°', 'Lon30', 'Amsā', 'Amsā Devatā', 
        'Sign', 'Bhava', 'Rāśi', 'Nakṣatra', 'Graha devatā', 'Pada', 'Speed'
    ]]
    out = chart_minimal(
        placements = p, 
        display_cols = [
            'Graha', 'Lon°', 'Amsā Devatā', 'Amsā', 'Nakṣatra', 
            'Graha devatā', 'Pada'
        ]
    )
    return out
