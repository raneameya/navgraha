# Ṣoḍaśāṃśa
from core.misc.misc_functions import add_non_equi_col, dms
import core.chart.chart as crt
from core.chart.chart_minimal import chart_minimal
from core.data.constants import rasis, rnp
from core.divisionals.divisional_helpers import add_house

amsa_devatās = {
    1:  ('Brahma', 'The Creator', 'Urge to create or acquire new possessions/vehicles'),
    2:  ('Viṣṇu', 'The Preserver', 'Ability to maintain, preserve, and stay attached to comforts'),
    3:  ('Shiva', 'The Destroyer', 'Potential for trouble, accidents, or damage to possessions'),
    4:  ('Sūrya', 'The Illuminator', 'Visible status and social appreciation of one\'s luxuries'),
    5:  ('Brahma', 'The Creator', 'Repeated cycle: focus on new material growth'),
    6:  ('Viṣṇu', 'The Preserver', 'Repeated cycle: focus on long-term utility of assets'),
    7:  ('Shiva', 'The Destroyer', 'Repeated cycle: points of friction or mechanical failure'),
    8:  ('Sūrya', 'The Illuminator', 'Repeated cycle: outward display of wealth and comfort'),
    9:  ('Brahma', 'The Creator', 'Expansion of domestic comforts and living standards'),
    10: ('Viṣṇu', 'The Preserver', 'Protection and security of one\'s home and transport'),
    11: ('Shiva', 'The Destroyer', 'Challenges or "wear and tear" in material life'),
    12: ('Sūrya', 'The Illuminator', 'Public recognition and prestige through luxury'),
    13: ('Brahma', 'The Creator', 'Creative efforts towards higher material ease'),
    14: ('Viṣṇu', 'The Preserver', 'Stability and contentment in one\'s environment'),
    15: ('Shiva', 'The Destroyer', 'Resolution of old assets or potential for losses'),
    16: ('Sūrya', 'The Illuminator', 'The pinnacle of satisfaction and visible prosperity')
}

def d16(birth_chart, type: str) -> chart_minimal:
    '''
    Compute the ṣoḍaśāṃśa (D-16) of a birth chart
    Args:
        birth_crt (chart): The base natal (D-1) chart.
    Returns:
        A chart_minimal object with the ṣoḍaśāṃśa placements including degrees
    '''
    d = 16
    p = birth_chart.rasi.placements.copy(deep = True)
    # Create a copy of sign in rasi. Used to classify whether graha in 
    # even/odd sign
    p['Natal sign'] = p['Sign']
    # Which amsa is a planet in? (i.e. 0, 1, 2, 3, ..., 15)
    p['Amsā'] = p['Lon30'].apply(lambda x: int(x // (30 / d)))
    # How much has the planet progressed in the amsā?
    if type == 'Parashari':
        # Aṃśa devata mapping is reversed if graha is in even sign in rāśi.
        p[['Lon30', 'Amsā Devatā']] = p.apply(
            lambda df: (
                (
                    (30 * ((df['Lon30'] / (30 / d)) % 1)),
                    amsa_devatās[df['Amsā'] + 1][0]
                    if df['Natal sign'] % 2 == 1 else
                    amsa_devatās[d - df['Amsā']][0]
                )
            ), axis = 1, result_type = 'expand'
        )
    elif type == 'Parashari reversed':
        # Progression and aṃśa devata mapping is reversed if
        # graha is in an even sign in rāśi.
        p[['Lon30', 'Amsā Devatā']] = p.apply(
            lambda df: (
                (
                    (30 * ((df['Lon30'] / (30 / d)) % 1)),
                    amsa_devatās[df['Amsā'] + 1][0]
                )
                if df['Natal sign'] % 2 == 1 else 
                (
                    30 - (30 * ((df['Lon30'] / (30 / d)) % 1)),
                    amsa_devatās[d - df['Amsā']][0]
                )
            ), axis = 1, result_type = 'expand'
        )
    def d16_progression(natal_rasi: int, amsa: int, type: str) -> int:
        # start_rasi is Aries for movable signs, Leo for fixed and
        # Sagittarius for dual signs
        start_rasi = [1, 5, 9][(natal_rasi - 1) % 3]
        if type == 'Parashari':
            return ((start_rasi - 1 + amsa) % 12) + 1
        elif type == 'Parashari reversed':
            if natal_rasi % 2 == 1:  # odd → forward
                return ((start_rasi - 1 + amsa) % 12) + 1
            else:  # even → backward
                # In this reversed version, we start at 4th from start_rasi
                # (why?) as opposed to starting from the rasi 12th from 
                # start_rasi. This matches results in JHora
                return ((start_rasi + 2 - amsa) % 12) + 1
    p['Sign'] = p.apply(
        lambda df: d16_progression(df['Natal sign'], df['Amsā'], type = type),
        axis = 1
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
