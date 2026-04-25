# Nakṣatrāṃśa
from core.misc.misc_functions import add_non_equi_col, dms
import core.chart.chart as crt
from core.chart.chart_minimal import chart_minimal
from core.data.constants import rasis, rnp
from core.divisionals.divisional_helpers import add_house

amsa_devatās = {
    1: ('Aśvinīkumāra', 'Healing', 'Divine physicians, vitality'),
    2: ('Yama', 'Justice', 'Dharma, discipline, restraint'),
    3: ('Agni', 'Purification', 'Sacred fire, transformation'),
    4: ('Brahmā', 'Creation', 'Creative intelligence, origin'),
    5: ('Soma', 'Nourishment', 'Lunar nectar, mental peace'),
    6: ('Rudra', 'Dissolution', 'Transformation through storm/force'),
    7: ('Aditi', 'Boundlessness', 'Mother of gods, protection'),
    8: ('Bṛhaspati', 'Wisdom', 'Guru of gods, spiritual knowledge'),
    9: ('Sarpa', 'Hidden Power', 'Serpents, mystical energy'),
    10: ('Pitṛ', 'Ancestry', 'Forefathers, lineage, tradition'),
    11: ('Bhaga', 'Fortune', 'Marital bliss, prosperity'),
    12: ('Aryaman', 'Partnership', 'Social cohesion, nobility'),
    13: ('Savitṛ', 'Inspiration', 'Solar energy, awakening'),
    14: ('Tvaṣṭṛ', 'Craftsmanship', 'Celestial architect, design'),
    15: ('Vāyu', 'Freedom', 'Wind, vital breath, movement'),
    16: ('Indrāgnī', 'Vitality', 'Dual power of leadership and fire'),
    17: ('Mitra', 'Friendship', 'Compassion, alliance, harmony'),
    18: ('Indra', 'Sovereignty', 'King of gods, power, protection'),
    19: ('Nirṛti', 'Rooting Out', 'Destruction for renewal, calamity'),
    20: ('Āpas', 'Fluidity', 'Cosmic waters, emotional healing'),
    21: ('Viśvedevāḥ', 'Universality', 'Collective virtues, integrity'),
    22: ('Viṣṇu', 'Sustenance', 'Preservation, pervasive wisdom'),
    23: ('Vasu', 'Abundance', 'Eight elemental deities, wealth'),
    24: ('Varuṇa', 'Cosmic Law', 'Guardian of waters, morality'),
    25: ('Ajaikapāda', 'Transcendence', 'One-footed goat, spiritual fire'),
    26: ('Ahirbudhnya', 'Depth', 'Serpent of the deep, foundation'),
    27: ('Pūṣan', 'Nurturing', 'Protector of journeys, safe passage')
}

def d27(birth_chart, type: str) -> chart_minimal:
    '''
    Compute the nakṣatrāṃśa (D-27) of a birth chart
    Args:
        birth_crt (chart): The base natal (D-1) chart.
    Returns:
        A chart_minimal object with the nakṣatrāṃśa placements including degrees
    '''
    d = 27
    p = birth_chart.rasi.placements.copy(deep = True)
    # Create a copy of sign in rasi. Used to classify whether graha in 
    # even/odd sign
    p['Natal sign'] = p['Sign']
    # Which amsa is a planet in? (i.e. 0, 1, 2, 3, ..., 26)
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
    def d27_progression(natal_rasi: int, amsa: int, type: str) -> int:
        # The start_sign of any sign maps to movable signs, though not of the 
        # same element as natal_rasi
        start_rasi_map = [1, 4, 7, 10] * 3
        start_rasi = start_rasi_map[natal_rasi - 1]
        if type == 'Parashari':
            return ((start_rasi - 1 + amsa) % 12) + 1
        elif type == 'Parashari reversed':
            if natal_rasi % 2 == 1:  # odd → forward
                return ((start_rasi - 1 + amsa) % 12) + 1
            else:  # even → backward
                # Typically, result is `((start_rasi - 1 - amsa) % 12) + 1`
                # However, this doesn't match JHora's results. There's an 
                # off by two relative to JHora's sign in nakṣatrāṃśa. Thus, 
                # have corrected for it with +1 instead of -1.
                return ((start_rasi + 1 - amsa) % 12) + 1
    p['Sign'] = p.apply(
        lambda df: d27_progression(df['Natal sign'], df['Amsā'], type = type),
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
