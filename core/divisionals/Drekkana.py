# Drekkāṇa
from core.misc.misc_functions import add_non_equi_col, dms, cyclic_shift
import core.chart.chart as crt
from core.chart.chart_minimal import chart_minimal
from core.data.constants import rasis, rnp
from core.divisionals.divisional_helpers import add_house

amsa_devata_map = {
    'movable': {1: 'Nārada', 2: 'Agastya', 3: 'Durvāsa'}, 
    'fixed': {1: 'Agastya', 2: 'Durvāsa', 3: 'Nārada'}, 
    'dual': {1: 'Durvāsa', 2: 'Nārada', 3: 'Agastya'}
}

def d3(birth_crt, type: str) -> chart_minimal:
    '''
    Compute the drekkāṇa (D-3) of a birth chart
    Args:
        birth_crt (chart): The natal (D-1) chart for which the drekkāṇa 
                        need to be computed.
        type (str): One of many different computation types for the varga
    Returns:
        A chart_minimal object with the drekkāṇa placements including degrees
    '''
    d = 3
    p = birth_crt.rasi.placements.copy(deep = True)
    # Create a copy of sign in rasi. Used to classify whether graha in 
    # even/odd sign
    p['Rasi sign'] = p['Sign']
    # Which amsa is a planet in? (i.e. 0-1)
    p['Amsā'] = p['Lon30'].apply(lambda x: int(x // (30 / d)))
    # How much has the planet progressed in the amsā? 
    # Classification of whether degrees are computed in reverse for even 
    # signs is matched to JHora's computation
    if type in ['Parashari', 'Parivṛtti', 'Jagannāth']:
        p['Lon30'] = p['Lon30'].apply(lambda x: (30 * ((x / (30 / d)) % 1)))
    elif type in ['Somanāth', 'Uma Shambhu']:
        # Progression is reversed if graha is in an even sign in rāśi
        p['Lon30'] = p.apply(lambda df: (
                30 * ((df['Lon30'] / (30 / d)) % 1) if df['Rasi sign'] % 2 != 0
                else 30 - (30 * ((df['Lon30'] / (30 / d)) % 1))
            ), axis = 1
        )
    def d3_progression(natal_rasi: int, amsa: int, type: str) -> int:
        if type == 'Parashari':
            # The 1st, 2nd & 3rd amsās are mapped to 1st, 5th & 9th from 
            # natal_rasi
            return ((natal_rasi - 1 + (4 * amsa)) % 12) + 1
        elif type == 'Parivṛtti':
            # Also called Parivṛtti-trayam. Similar cyclical mapping as in 
            # other parivṛtti vargas.
            start_rasi = (((natal_rasi - 1) * 3) % 12) + 1
            return (start_rasi + amsa)
        elif type == 'Uma Shambhu':
            # This is the Uma-Shambhu mapping as stated by PVR. 
            # This is a variation of the Parivṛtti mapping as above, 
            # except that for even signs, the mapping is reversed. So, instead of 
            # Taurus mapping to Ge & Cn, it would map to Cn & Ge. Similarly, 
            # Virgo would map to Pi & Aq. Odd signs are the same as regular 
            # Parivṛtti.
            start_rasi = (((natal_rasi - 1) * 3) % 12) + 1
            if natal_rasi % 2 == 1: # Odd sign, forward
                return start_rasi + amsa
            else: # Even sign, backward
                return ((start_rasi - amsa + 1) % 12) + 1
        elif type == 'Jagannāth':
            # start_rasi is the movable rasi of the same element. Next, the 
            # 1st, 2nd & 3rd amsās are mapped to 1st, 5th & 9th from start_rasi
            start_rasi_map = [1, 10, 7, 4] * 3
            start_rasi = start_rasi_map[natal_rasi - 1]
            return ((start_rasi - 1 + (4 * amsa)) % 12) + 1
        elif type == 'Somanāth':
            # Don't fully understand the start_rasi logic. Indebted to 
            # Prof. Dr. NS Murthy and his prsentation:
            # https://www.scribd.com/presentation/511597621/Drekkanaas
            start_rasi_map = [1, 12, 4, 9, 7, 6, 10, 3, 1, 12, 4, 9]
            start_rasi = start_rasi_map[natal_rasi - 1]
            if natal_rasi % 2 == 1: # Odd sign, forward
                return start_rasi + amsa
            else: # Even sign, backward
                return ((start_rasi - amsa - 1) % 12) + 1
    p['Sign'] = p.apply(
        lambda df: d3_progression(
            df['Rasi sign'], df['Amsā'], type = type
        ), axis = 1
    )
    # amsā devata reorder
    def amsā_reorder(natal_rasi):
        # Movable rasis have same order
        if natal_rasi in [1, 4, 7, 10]:
            return amsa_devata_map['movable']
        elif natal_rasi in [2, 5, 8, 11]:
            return amsa_devata_map['fixed']
        elif natal_rasi in [3, 6, 9, 12]:
            return amsa_devata_map['dual']
    # Pull in info about amsā devata
    p['Amsā Devatā'] = p.apply(
        lambda df: (
            amsā_reorder(df['Rasi sign'])[df['Amsā'] + 1]
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
            'Graha', 'Lon°', 'Amsā Devatā', 'Nakṣatra', 
            'Graha devatā', 'Pada'
        ]
    )
    return out
