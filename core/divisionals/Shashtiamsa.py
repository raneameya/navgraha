# Ṣaṣṭyāṃśa
from core.misc.misc_functions import add_non_equi_col, dms
import core.chart.chart as crt
from core.chart.chart_minimal import chart_minimal
from core.data.constants import rasis, rnp
from core.divisionals.divisional_helpers import add_house

amsa_devata_mapping = {
    1: ('Ghora', 'घोर', 'Terrible, fierce'),
    2: ('Rākṣasa', 'राक्षस', 'Demonic'),
    3: ('Deva', 'देव', 'Divine, shining'),
    4: ('Kubera', 'कुबेर', 'God of wealth'),
    5: ('Yakṣa', 'यक्ष', 'Celestial guardian'),
    6: ('Kinnara', 'किन्नर', 'Celestial musician'),
    7: ('Bhraṣṭa', 'भ्रष्ट', 'Fallen, corrupt'),
    8: ('Kulaghna', 'कुलघ्न', 'Family destroyer'),
    9: ('Garala', 'गरल', 'Poison'),
    10: ('Vahni', 'वह्नि', 'Fire'),
    11: ('Māyā', 'माया', 'Illusion, deceit'),
    12: ('Purīṣaka', 'पुरीषक', 'Dirty, soiled'),
    13: ('Apāmpati', 'अपाम्पति', 'Lord of waters (Varuṇa)'),
    14: ('Marutvān', 'मरुत्वान्', 'Lord of wind'),
    15: ('Kāla', 'काल', 'Time'),
    16: ('Sarpa', 'सर्प', 'Serpent'),
    17: ('Amṛta', 'अमृत', 'Nectar of immortality'),
    18: ('Indu', 'इन्दु', 'Moon'),
    19: ('Mṛdu', 'मृदु', 'Soft, tender'),
    20: ('Komala', 'कोमल', 'Gentle, delicate'),
    21: ('Heramba', 'हेरम्ब', 'A form of Ganesha'),
    22: ('Brahmā', 'ब्रह्मा', 'The Creator'),
    23: ('Viṣṇu', 'विष्णु', 'The Preserver'),
    24: ('Maheśvara', 'महेश्वर', 'The Destroyer (Shiva)'),
    25: ('Deva', 'देव', 'Radiant one'),
    26: ('Ārdra', 'आर्द्र', 'Moist, wet'),
    27: ('Kalināśa', 'कलिनाश', 'Destroyer of strife'),
    28: ('Kṣitīśa', 'क्षितीश', 'Lord of the Earth'),
    29: ('Kamalākara', 'कमलाकर', 'Lotus pond'),
    30: ('Gulika', 'गुलिका', 'Son of Saturn (malefic)'),
    31: ('Mṛtyu', 'मृत्यु', 'Death'),
    32: ('Kāla', 'काल', 'Time'),
    33: ('Davāgni', 'दवाग्नि', 'Forest fire'),
    34: ('Ghora', 'घोर', 'Terrible'),
    35: ('Yama', 'यम', 'God of death'),
    36: ('Kaṇṭaka', 'कण्टक', 'Thorn'),
    37: ('Śuddha', 'शुद्ध', 'Pure'),
    38: ('Amṛta', 'अमृत', 'Nectar'),
    39: ('Pūrṇacandra', 'पूर्णचन्द्र', 'Full moon'),
    40: ('Viṣadagdha', 'विषदग्ध', 'Consumed by poison'),
    41: ('Kulanāśa', 'कुलनाश', 'Destroyer of lineage'),
    42: ('Vaṃśakṣaya', 'वंशक्षय', 'Loss of family'),
    43: ('Utpāta', 'उत्पात', 'Calamity, chaos'),
    44: ('Kāla', 'काल', 'Time'),
    45: ('Saumya', 'सौम्य', 'Gentle, benefic'),
    46: ('Komala', 'कोमल', 'Delicate'),
    47: ('Śītala', 'शीतल', 'Cold, soothing'),
    48: ('Karāladamṣṭra', 'करालदंष्ट्र', 'Fierce-toothed'),
    49: ('Candramukhī', 'चन्द्रमुखी', 'Moon-faced'),
    50: ('Pravīṇa', 'प्रवीण', 'Expert, skilled'),
    51: ('Kālapāvaka', 'कालपावक', 'Time\'s fire'),
    52: ('Daṇḍāyudha', 'दण्डायुध', 'Staff weapon'),
    53: ('Nirmala', 'निर्मल', 'Spotless, pure'),
    54: ('Saumya', 'सौम्य', 'Benefic'),
    55: ('Krūra', 'क्रूर', 'Cruel'),
    56: ('Atiśītala', 'अतिशीतल', 'Extremely cold'),
    57: ('Amṛta', 'अमृत', 'Nectar'),
    58: ('Payodhi', 'पयोधि', 'Ocean'),
    59: ('Brahman', 'ब्रह्मन्', 'Universal soul or Wanderer'),
    60: ('Candrarekhā', 'चन्द्ररेखा', 'Streak of the moon')    
}

def d60(birth_chart, type: str) -> chart_minimal:
    '''
    Compute the ṣaṣṭyāṃśa (D-60) of a birth chart
    Args:
        birth_crt (chart): The base natal (D-1) chart.
    Returns:
        A chart_minimal object with the ṣaṣṭyāṃśa placements including degrees
    '''
    p = birth_chart.rasi.placements.copy(deep = True)
    # Create a copy of sign in rasi. Used to classify whether graha in 
    # even/odd sign
    p['Natal sign'] = p['Sign']
    # Which amsa is a planet in? (i.e. 0, 1, 2, ... 59)
    p['Amsā'] = p['Lon30'].apply(lambda x: int(x // (30/60)))
    # Pull in info about amsā devata. Reverse pull if graha is in 
    # even sign natally
    p['Amsā Devatā'] = p.apply(
        lambda df: (
            amsa_devata_mapping[df['Amsā'] + 1][0] 
            if df['Natal sign'] % 2 == 1
            else amsa_devata_mapping[60 - df['Amsā']][0] 
        ), 
        axis = 1
    )
    # How much has the planet progressed in the amsā?
    if type == 'Traditional Parashari':
        p['Lon30'] = p['Lon30'].apply(lambda x: 30*((x / (30 / 60)) % 1))
    elif type == 'Parashari reversed':
        p['Lon30'] = p.apply(lambda df: (
                30 * ((df['Lon30'] / (30 / 60)) % 1) 
                if df['Natal sign'] % 2 != 0
                else 30 - (30 * ((df['Lon30'] / (30 / 60)) % 1))
            ), axis = 1
        )
    def d60_progression(natal_rasi: int, amsa: int , type: str) -> int:
        if type == 'Traditional Parashari':
            ṣaṣṭyāṃśa_rasi = int((natal_rasi + amsa) % 12)
        elif type == 'Parashari reversed': # Even sign reversal
            if natal_rasi % 2 == 1:
                ṣaṣṭyāṃśa_rasi = int((natal_rasi + amsa) % 12)
            else:
                x = int((natal_rasi - amsa - 1) % 12)
                ṣaṣṭyāṃśa_rasi = 12 if x == 0 else x                
        return ṣaṣṭyāṃśa_rasi
    p['Sign'] = p.apply(
        lambda df: d60_progression(
            df['Natal sign'], df['Amsā'], type = type
        ), axis = 1
    )
    p['Rāśi'] = p['Sign'].apply(lambda x: list(rasis['Rāśi'])[x - 1])
    p['Lon°'] = p['Lon30'].apply(lambda x: dms(degrees = x))
    p['Lon'] = p.apply(lambda x: x['Lon30'] + 30 * x['Sign'] - 30, axis = 1)
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
