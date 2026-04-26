# Siddhāṃśa
from core.misc.misc_functions import add_non_equi_col, dms
import core.chart.chart as crt
from core.chart.chart_minimal import chart_minimal
from core.data.constants import rasis, rnp
from core.divisionals.divisional_helpers import add_house

amsa_devatās = {
    # 12 devatās repeated twice in cyclical order. Order reversed for even signs
    1:  ('Skanda', 'Celestial General', 'Leadership, focus, and strategic intelligence'),
    2:  ('Paraśudhāra', 'Axe-Wielder', 'Incisive logic, discipline, and removing ignorance'),
    3:  ('Anala', 'Sacred Fire', 'Transformation, digestive power of the mind, and clarity'),
    4:  ('Viśvakarmā', 'Divine Architect', 'Creative skill, craftsmanship, and technical mastery'),
    5:  ('Bhaga', 'Lord of Fortune', 'Inherited wealth of knowledge and auspicious learning'),
    6:  ('Mitra', 'The Friend', 'Collaborative wisdom, harmony, and social sciences'),
    7:  ('Maya', 'The Illusionist', 'Deep technical knowledge, secrets, and architecture'),
    8:  ('Antaka', 'The Ender', 'Death of ignorance, deep research, and finality'),
    9:  ('Vṛṣadhvaja', 'One with the Bull Flag', 'Dharma, ethics, and steady traditional knowledge'),
    10: ('Govinda', 'The Herder/Protector', 'Preservation of wisdom and nurturing of skills'),
    11: ('Madana', 'Lord of Desire', 'Creative passion, arts, and aesthetic intelligence'),
    12: ('Bhīma', 'The Mighty', 'Immense strength, protection, and physical mastery'),
    13: ('Skanda', 'Celestial General', 'Advanced leadership and strategic refinement'),
    14: ('Paraśudhāra', 'Axe-Wielder', 'Further refinement of critical thinking'),
    15: ('Anala', 'Sacred Fire', 'Higher spiritual illumination and digestion of truth'),
    16: ('Viśvakarmā', 'Divine Architect', 'Complex structural and cosmic understanding'),
    17: ('Bhaga', 'Lord of Fortune', 'Culmination of fortune in higher learning'),
    18: ('Mitra', 'The Friend', 'Global or universal connections in wisdom'),
    19: ('Maya', 'The Illusionist', 'Advanced mystical or hidden scientific fields'),
    20: ('Antaka', 'The Ender', 'Completion of a cycle of profound research'),
    21: ('Vṛṣadhvaja', 'One with the Bull Flag', 'Establishment of enduring spiritual dharma'),
    22: ('Govinda', 'The Herder/Protector', 'Universal guardianship of sacred knowledge'),
    23: ('Madana', 'Lord of Desire', 'Joy and bliss found in perfected knowledge'),
    24: ('Bhīma', 'The Mighty', 'The ultimate strength of an accomplished scholar')
}


def d24(birth_chart, type: str) -> chart_minimal:
    '''
    Compute the siddhāṃśa (D-24) of a birth chart
    Args:
        birth_crt (chart): The base natal (D-1) chart.
    Returns:
        A chart_minimal object with the siddhāṃśa placements including degrees
    '''
    d = 24
    p = birth_chart.rasi.placements.copy(deep = True)
    # Create a copy of sign in rasi. Used to classify whether graha in 
    # even/odd sign
    p['Natal sign'] = p['Sign']
    # Which amsa is a planet in? (i.e. 0, 1, 2, 3, ..., 23)
    p['Amsā'] = p['Lon30'].apply(lambda x: int(x // (30 / d)))
    # How much has the planet progressed in the amsā?
    if type == 'Parashari':
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
    def d24_progression(natal_rasi: int, amsa: int, type: str) -> int:
        # start_rasi is Leo for odd signs and Cancer for even signs
        start_rasi = [4, 5][natal_rasi % 2]
        if type == 'Parashari':
            return ((start_rasi - 1 + amsa) % 12) + 1
        elif type == 'Parashari reversed':
            if natal_rasi % 2 == 1:  # odd → forward
                return ((start_rasi - 1 + amsa) % 12) + 1
            else:  # even → backward
                # In this reversed version, we start at start_rasi itself
                # as opposed to starting from the rasi 12th from start_rasi.
                return ((start_rasi - 1 - amsa) % 12) + 1
    p['Sign'] = p.apply(
        lambda df: d24_progression(df['Natal sign'], df['Amsā'], type = type),
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
