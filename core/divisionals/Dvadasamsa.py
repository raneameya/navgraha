# Dvādaśāṃśa
from core.misc.misc_functions import add_non_equi_col, dms
import core.chart.chart as crt
from core.chart.chart_minimal import chart_minimal
from core.data.constants import rasis, rnp
from core.divisionals.divisional_helpers import add_house

amsa_devatās = {
    1: ('Gaṇeśa', 'Lord of Beginnings', 'Remover (or creator) of obstacles, creative origin'),
    2: ('Aśvinīkumāra', 'Divine Physicians', 'Healing, vitality, and preservation of lineage'),
    3: ('Yama', 'Lord of Dharma', 'Restraint, discipline, and the ending of karmic cycles'),
    4: ('Ahi', 'The Serpent', 'Hidden wisdom, ancestral depths, and deep-seated desires'),
    5: ('Gaṇeśa', 'Lord of Beginnings', 'focus on ancestral creative power'),
    6: ('Aśvinīkumāra', 'Divine Physicians', 'focus on inherited health/vitality'),
    7: ('Yama', 'Lord of Dharma', 'focus on family duties and justice'),
    8: ('Ahi', 'The Serpent', 'focus on secret family karma'),
    9: ('Gaṇeśa', 'Lord of Beginnings', 'final stage of creative lineage'),
    10: ('Aśvinīkumāra', 'Divine Physicians', 'final stage of preservation'),
    11: ('Yama', 'Lord of Dharma', 'final stage of detachment/restraint'),
    12: ('Ahi', 'The Serpent', 'completion of ancestral influence')
}

def d12(birth_chart, type: str) -> chart_minimal:
    '''
    Compute the dvādaśāṃśa (D-12) of a birth chart
    Args:
        birth_crt (chart): The base natal (D-1) chart.
    Returns:
        A chart_minimal object with the dvādaśāṃśa placements including degrees
    '''
    d = 12
    p = birth_chart.rasi.placements.copy(deep = True)
    # Create a copy of sign in rasi. Used to classify whether graha in 
    # even/odd sign
    p['Natal sign'] = p['Sign']
    # Which amsa is a planet in? (i.e. 0, 1, 2, 3, ..., 11)
    p['Amsā'] = p['Lon30'].apply(lambda x: int(x // (30 / d)))
    # How much has the planet progressed in the amsā?
    if type == 'Parashari':
        p[['Lon30', 'Amsā Devatā']] = p.apply(
            lambda df: (
                (
                    (30 * ((df['Lon30'] / (30 / d)) % 1)),
                    amsa_devatās[df['Amsā'] + 1][0]
                )
            ), axis = 1, result_type = 'expand'
        )
    elif type == 'Parashari reversed':
        # Progression is reversed if graha is in an even sign in rāśi.
        # Amsā Devatā mapping is unaffected.
        p[['Lon30', 'Amsā Devatā']] = p.apply(
            lambda df: (
                (
                    (30 * ((df['Lon30'] / (30 / d)) % 1))
                    if df['Natal sign'] % 2 == 1 else 
                    30 - (30 * ((df['Lon30'] / (30 / d)) % 1)),
                    amsa_devatās[df['Amsā'] + 1][0]
                )
            ), axis = 1, result_type = 'expand'
        )
    def d12_progression(natal_rasi: int, amsa: int, type: str) -> int:
        if type == 'Parashari':
            return ((natal_rasi - 1 + amsa) % 12) + 1
        elif type == 'Parashari reversed':
            if natal_rasi % 2 == 1:  # odd → forward
                return ((natal_rasi - 1 + amsa) % 12) + 1
            else:  # even → backward
                # Counting backwards in JHora is done from the rasi prior to
                # natal_rasi. Thus, the 1st aṃśa (or 0th, if 0 based as is 
                # the case here) maps to natal_rasi - 1 and the 12th aṃśa 
                # maps to itself.
                return ((natal_rasi - 2 - amsa) % 12) + 1
    p['Sign'] = p.apply(
        lambda df: d12_progression(df['Natal sign'], df['Amsā'], type = type),
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
