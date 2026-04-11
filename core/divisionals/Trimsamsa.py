# Triṃśāṃśa
from core.misc.misc_functions import add_non_equi_col, dms
import core.chart.chart as crt
from core.chart.chart_minimal import chart_minimal
from core.data.constants import rasis, rnp
from core.divisionals.divisional_helpers import add_house

amsa_devatas = {
    # amsa: (devatā, mahābhūta, graha, guṇa, psr_odd_triṃś, psr_even_triṃś)
    1: ('Agni', 'Tejas', 'Maṅgala', 'Vitality/Transformation', 1, 8),
    6: ('Vāyu', 'Vāyu', 'Śani', 'Movement/Dryness', 11, 10),
    11: ('Indra', 'Ākāśa', 'Guru', 'Expansion/Authority', 9, 12),
    19: ('Kubera', 'Pṛthvī', 'Budha', 'Fluidity/Binding', 3, 6),
    26: ('Varuṇa', 'Jala', 'Śukra', 'Stability/Form', 7, 2)
}
amsa_devatas = {
    # For odd signs only. Reverse the dict for even signs
    (k + 1): amsa_devatas[
        max(filter(lambda x: x <= (k + 1), amsa_devatas.keys()))
    ] for k in range(30)
}

'''
# Does this have any basis? From Google Gemini:
parivṛtti_amsa_devata = {
    1: ("Yama", "Restraint/Death", "Dharamarāja"),
    2: ("Niśācara", "Night-walker/Ghost", "Tāmasika"),
    3: ("Murari", "Enemy of Mura (Viṣṇu)", "Sāttvika"),
    4: ("Jala", "Water/Varuṇa", "Fluidity"),
    5: ("Vāyu", "Wind", "Movement"),
    6: ("Kubera", "Wealth", "Materialism"),
    7: ("Vināyaka", "Remover of Obstacles (Gaṇeśa)", "Wisdom"),
    8: ("Surarāja", "King of Gods (Indra)", "Power"),
    9: ("Purūravas", "Mythological King", "Passion"),
    10: ("Vṛṣadhvaja", "Bull-bannered (Śiva)", "Asceticism"),
    11: ("Kāla", "Time/Destiny", "Endings"),
    12: ("Vāsava", "Indra/Abundance", "Protection"),
    13: ("Amṛta", "Nectar of Immortality", "Healing"),
    14: ("Ananta", "Infinite (Śeṣanāga)", "Stability"),
    15: ("Candra", "Moon", "Nurturing"),
    16: ("Viṣṇu", "The Preserver", "Maintenance"),
    17: ("Ajapāda", "Unborn foot (Ekapāda Rudra)", "Mysticism"),
    18: ("Ahirbudhnya", "Serpent of the Deep", "Foundational"),
    19: ("Pitṛ", "Ancestors", "Lineage"),
    20: ("Vāruṇa", "Oceanic/Law", "Judgment"),
    21: ("Indra", "Sensory Lord", "Enjoyment"),
    22: ("Viśvakarman", "Divine Architect", "Creation"),
    23: ("Abhijit", "Victorious", "Success"),
    24: ("Vidhi", "Creator/Brahmā", "Order"),
    25: ("Vāmana", "The Dwarf Avatar", "Humility"),
    26: ("Dhanvantarī", "Physician of Gods", "Health"),
    27: ("Sūrya", "Sun", "Soul/Light"),
    28: ("Mṛtyu", "Death/Transition", "Transformation"),
    29: ("Śiva", "The Destroyer", "Liberation"),
    30: ("Vasiṣṭha", "The Great Sage", "Enlightenment")
}
'''

def d30(birth_chart, type: str) -> chart_minimal:
    '''
    Compute the triṃśāṃśa (D-30) of a birth chart
    Args:
        birth_crt (chart): The base natal (D-1) chart.
    Returns:
        A chart_minimal object with the triṃśāṃśa placements including degrees
    '''
    d = 30
    p = birth_chart.rasi.placements.copy(deep = True)
    # Create a copy of sign in rasi. Used to classify whether graha in 
    # even/odd sign
    p['Natal sign'] = p['Sign']
    # Which amsa is a planet in? (i.e. 0, 1, 2, 3)
    p['Amsā'] = p['Lon30'].apply(lambda x: int(x // (30 / d)))
    # How much has the planet progressed in the amsā?
    p['Lon30'] = p['Lon30'].apply(lambda x: 30 * ((x / (30 / d)) % 1))
    if type == 'Parashari':
        # Pull in info about amsā devata & sign. Reverse pull if graha is in 
        # even sign natally
        p[['Amsā Devatā', 'Sign']] = p.apply(
            lambda df: (
                (
                    # Odd natal sign
                    amsa_devatas[df['Amsā'] + 1][0], 
                    amsa_devatas[df['Amsā'] + 1][4]
                )
                if df['Natal sign'] % 2 == 1
                else (
                    # Even natal sign
                    amsa_devatas[d - df['Amsā']][0],
                    amsa_devatas[d - df['Amsā']][5]
                )
            ), 
            axis = 1, result_type='expand'
        )
    elif type == 'Parivṛtti':
        # Currently using Parashari amsa devatas. Are they different for 
        # Parivṛtti?
        p['Amsā Devatā'] = p.apply(
            lambda df: (
                amsa_devatas[df['Amsā'] + 1][0]
                if df['Natal sign'] % 2 == 1
                else amsa_devatas[d - df['Amsā']][0]
            ), 
            axis = 1
        )
        def d30_progression(natal_rasi: int, amsa: int) -> int:
            start_rasi = 1 if natal_rasi % 2 == 1 else 7
            return ((start_rasi - 1 + amsa) % 12) + 1
        p['Sign'] = p.apply(
            lambda df: d30_progression(df['Natal sign'], df['Amsā']), axis = 1
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
