# Daśāṃśa
from core.misc.misc_functions import add_non_equi_col, dms
import core.chart.chart as crt
from core.chart.chart_minimal import chart_minimal
from core.data.constants import rasis, rnp
from core.divisionals.divisional_helpers import add_house

amsa_devata_mapping = {
    1: ('Indra', 'Pūrva (East)', 'Power and Leadership'),
    2: ('Agni', 'Āgneya (Southeast)', 'Transformation and Energy'),
    3: ('Yama', 'Dakṣiṇa (South)', 'Discipline and Justice'),
    4: ('Rākṣasa', 'Nairṛta (Southwest)', 'Removal of Obstacles'),
    5: ('Varuṇa', 'Paścima (West)', 'Strategy and Management'),
    6: ('Vāyu', 'Vāyavya (Northwest)', 'Networking and Movement'),
    7: ('Kubera', 'Uttara (North)', 'Wealth and Resources'),
    8: ('Īśāna', 'Aiśānya (Northeast)', 'Mentorship and Knowledge'),
    9: ('Brahmā', 'Ūrdhva (Zenith)', 'Innovation and Creation'),
    10: ('Ananta', 'Adhaḥ (Nadir)', 'Stability and Support')
}

def d10(birth_chart, type: str) -> chart_minimal:
    '''
    Compute the daśāṃśa (D-10) of a birth chart
    Args:
        birth_crt (chart): The base natal (D-1) chart.
    Returns:
        A chart_minimal object with the daśāṃśa placements including degrees
    '''
    p = birth_chart.rasi.placements.copy(deep = True)
    # Create a copy of sign in rasi. Used to classify whether graha in 
    # even/odd sign
    p['Natal sign'] = p['Sign']
    # Which amsa is a planet in? (i.e. 0, 1, 2, ... 9)
    p['Amsā'] = p['Lon30'].apply(lambda x: int(x // (30/10)))
    # Pull in info about amsā devata. Reverse pull if graha is in 
    # even sign natally
    p['Amsā Devatā'] = p.apply(
        lambda df: (
            amsa_devata_mapping[df['Amsā'] + 1][0]
            if df['Natal sign'] % 2 == 1
            else amsa_devata_mapping[10 - df['Amsā']][0]
        ), 
        axis = 1
    )
    # How much has the planet progressed in the amsā?
    if type == 'Parashari':
        p['Lon30'] = p['Lon30'].apply(lambda x: 30*((x / (30 / 10)) % 1))
    elif type in ['Parashari reversed', 'Parashari reversed (6-9)']:
        p['Lon30'] = p.apply(lambda df: (
                30 * ((df['Lon30'] / (30 / 10)) % 1) 
                if df['Natal sign'] % 2 != 0
                else 30 - (30 * ((df['Lon30'] / (30 / 10)) % 1))
            ), axis = 1
        )
    def d10_progression(natal_rasi: int, amsa: int, type: str) -> int:
        if natal_rasi % 2 == 1:
            # For all variations, if natal sign is odd, progression 
            # is forward starting from natal rasi
            return ((natal_rasi - 1 + amsa) % 12) + 1
        else:
            # Different variations of progression if natal sign is even
            if type == 'Parashari':        
                # start from 9th sign from natal sign and go forward
                return ((natal_rasi + 8 - 1 + amsa) % 12) + 1
            elif type == 'Parashari reversed':
                # as above, but progression is reversed
                return ((natal_rasi + 8 - 1 - amsa) % 12) + 1
            elif type == 'Parashari reversed (6-9)':
                # end in 9th sign from natal sign with progression reversed
                return ((natal_rasi + 5 - 1 - amsa) % 12) + 1
    p['Sign'] = p.apply(
        lambda df: d10_progression(
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
