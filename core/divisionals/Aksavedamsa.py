# Akṣavedāṃśa
from core.misc.misc_functions import add_non_equi_col, dms
import core.chart.chart as crt
from core.chart.chart_minimal import chart_minimal
from core.data.constants import rasis, rnp
from core.divisionals.divisional_helpers import add_house

amsa_devatās = {
    'movable': {1: 'Brahmā', 2: 'Śiva', 3: 'Viṣṇu'}, 
    'fixed': {1: 'Śiva', 2: 'Viṣṇu', 3: 'Brahmā'}, 
    'dual': {1: 'Viṣṇu', 2: 'Brahmā', 3: 'Śiva'}
}

def d45(birth_chart) -> chart_minimal:
    '''
    Compute the akṣavedāṃśa (D-45) of a birth chart
    Args:
        birth_crt (chart): The base natal (D-1) chart.
    Returns:
        A chart_minimal object with the akṣavedāṃśa placements including degrees
    '''
    d = 45
    p = birth_chart.rasi.placements.copy(deep = True)
    # Create a copy of sign in rasi. Used to classify whether graha in 
    # even/odd sign
    p['Natal sign'] = p['Sign']
    # Which āṃśa is a planet in? (i.e. 0, 1, 2, 3, ..., 44)
    p['Amsā'] = p['Lon30'].apply(lambda x: int(x // (30 / d)))
    # āṃśa devata reorder
    def āṃśa_reorder(natal_rasi):
        # Movable rasis have same order
        if natal_rasi in [1, 4, 7, 10]:
            return amsa_devatās['movable']
        elif natal_rasi in [2, 5, 8, 11]:
            return amsa_devatās['fixed']
        elif natal_rasi in [3, 6, 9, 12]:
            return amsa_devatās['dual']
    # How much has the planet progressed in the āṃśa?
    p[['Lon30', 'Amsā Devatā']] = p.apply(
        lambda df: (
            (
                (30 * ((df['Lon30'] / (30 / d)) % 1)),
                āṃśa_reorder(df['Natal sign'])[(df['Amsā'] % 3) + 1]
            )
        ), axis = 1, result_type = 'expand'
    )
    def d45_progression(natal_rasi: int, amsa: int) -> int:
        # start_rasi is Aries for movable signs, Leo for fixed and
        # Sagittarius for dual signs
        start_rasi = [1, 5, 9][(natal_rasi - 1) % 3]
        return ((start_rasi - 1 + amsa) % 12) + 1
    p['Sign'] = p.apply(
        lambda df: d45_progression(df['Natal sign'], df['Amsā']), axis = 1
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
