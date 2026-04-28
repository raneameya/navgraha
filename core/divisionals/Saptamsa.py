# Saptāṃśa
from core.misc.misc_functions import add_non_equi_col, dms
import core.chart.chart as crt
from core.chart.chart_minimal import chart_minimal
from core.data.constants import rasis, rnp
from core.divisionals.divisional_helpers import add_house

āṃśa_devatās = {
    1: ('Kṣāra', 'Salt/Alkaline', 'Represents challenges, pungency, or initial friction in matters of progeny'),
    2: ('Kṣīra', 'Milk', 'Represents nourishment, purity, and the growth of the lineage'),
    3: ('Dadhi', 'Curd', 'Represents stability, solidification of family roots, and health'),
    4: ('Ghṛta', 'Ghee/Clarified Butter', 'Represents the essence, prosperity, and refinement of one\'s children'),
    5: ('Ikṣurasa', 'Sugarcane Juice', 'Represents sweetness, joy, and the creative energy of the offspring'),
    6: ('Surā', 'Wine/Spirituous Liquor', 'Represents intoxication, stimulation, or potentially hidden traits'),
    7: ('Śuddha Jala', 'Nectar/Ambrosia', 'Represents the highest blessing, longevity, and spiritual success of progeny')
}

def d7(birth_chart, type: str) -> chart_minimal:
    '''
    Compute the saptāṃśa (D-16) of a birth chart
    Args:
        birth_crt (chart): The base natal (D-1) chart.
    Returns:
        A chart_minimal object with the saptāṃśa placements including degrees
    '''
    d = 7
    p = birth_chart.rasi.placements.copy(deep = True)
    # Create a copy of sign in rasi. Used to classify whether graha in 
    # even/odd sign
    p['Natal sign'] = p['Sign']
    # Which amsa is a planet in? (i.e. 0, 1, 2, 3, ..., 6)
    p['Amsā'] = p['Lon30'].apply(lambda x: int(x // (30 / d)))
    # How much has the planet progressed in the amsā?
    if type == 'Parashari':
        # Aṃśa devata mapping is reversed if graha is in even sign in rāśi.
        p[['Lon30', 'Amsā Devatā']] = p.apply(
            lambda df: (
                (
                    (30 * ((df['Lon30'] / (30 / d)) % 1)),
                    āṃśa_devatās[df['Amsā'] + 1][0]
                    if df['Natal sign'] % 2 == 1 else
                    āṃśa_devatās[d - df['Amsā']][0]
                )
            ), axis = 1, result_type = 'expand'
        )
    elif type in ['Parashari reversed (1-7)', 'Parashari reversed (7-1)']:
        # Progression and aṃśa devata mapping is reversed if
        # graha is in an even sign in rāśi.
        p[['Lon30', 'Amsā Devatā']] = p.apply(
            lambda df: (
                (
                    (30 * ((df['Lon30'] / (30 / d)) % 1)),
                    āṃśa_devatās[df['Amsā'] + 1][0]
                )
                if df['Natal sign'] % 2 == 1 else 
                (
                    30 - (30 * ((df['Lon30'] / (30 / d)) % 1)),
                    āṃśa_devatās[d - df['Amsā']][0]
                )
            ), axis = 1, result_type = 'expand'
        )
    def d7_progression(natal_rasi: int, amsa: int, type: str) -> int:
        # start_rasi is same sign for odd natal_rasi, but 7th from natal_rasi
        # if even
        is_odd = natal_rasi % 2
        start_rasi = natal_rasi if is_odd else ((natal_rasi + 5) % 12) + 1
        if is_odd:
            return ((start_rasi - 1 + amsa) % 12) + 1
        else:
            if type == 'Parashari':
                x = ((start_rasi - 1 + amsa) % 12) + 1
                return ((start_rasi - 1 + amsa) % 12) + 1
            elif type == 'Parashari reversed (1-7)': # even → backward
                # In this reversed version, we start from 7th from start_rasi, 
                # which is natal_rasi
                return ((natal_rasi - 1 - amsa) % 12) + 1
            elif type == 'Parashari reversed (7-1)': # even → backward
                # In this reversed version, we start from start_rasi
                return ((start_rasi - 1 - amsa) % 12) + 1
    p['Sign'] = p.apply(
        lambda df: d7_progression(df['Natal sign'], df['Amsā'], type = type),
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
