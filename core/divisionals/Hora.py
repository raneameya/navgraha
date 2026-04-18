from core.misc.misc_functions import add_non_equi_col, dms
import core.chart.chart as crt
from core.chart.chart_minimal import chart_minimal
from core.data.constants import rasis, rnp
from core.divisionals.divisional_helpers import add_house

amsa_devata_mapping = {
    1: 'Devās - Sun', 2: 'Pitṛs - Moon'
}
amsa_devata_mapping_rev = {
    1: 'Pitṛs - Moon', 2: 'Devās - Sun'
}

def d2(birth_crt, type: str) -> chart_minimal:
    '''
    Compute the hora (D-2) of a birth chart
    Args:
        birth_crt (chart): The natal (D-1) chart for which the hora need to be computed.
    Returns:
        A chart_minimal object with the hora placements including degrees
    '''
    d = 2
    p = birth_crt.rasi.placements.copy(deep = True)
    # Create a copy of sign in rasi. Used to classify whether graha in 
    # even/odd sign
    p['Rasi sign'] = p['Sign']
    # Which amsa is a planet in? (i.e. 0-1)
    p['Amsā'] = p['Lon30'].apply(lambda x: int(x // (30 / d)))
    # How much has the planet progressed in the amsā? 
    # Classification of whether degrees are computed in reverse for even 
    # signs is matched to JHora's computation
    if type in [
        'Parashari', 'Parivṛtti', 'Kāśīnāth', 'Jagannāth', 'Samasaptaka',
        'Maṇḍūka', 'Lābha maṇḍūka'
    ]:
        p['Lon30'] = p['Lon30'].apply(lambda x: (30 * ((x / (30 / d)) % 1)))
    elif type in ['Uma Shambhu']:
        # Progression is reversed if graha is in an even sign in rāśi
        p['Lon30'] = p.apply(lambda df: (
                30 * ((df['Lon30']/(30 / d)) % 1) if df['Rasi sign'] % 2 != 0
                else 30 - (30 * ((df['Lon30']/(30 / d)) % 1))
            ), axis = 1
        )
    # Compute hora index (0-23) based on the sign and the half of the sign 
    # in which the graha is. (e.g. 23°30' Ge maps to 5). This is NOT the amsa 
    # which is the index within a sign.
    p['Hora index'] = p.apply(
        lambda df: (df['Sign'] - 1) * 2 + df['Amsā'], axis = 1
    )
    if type == 'Parashari':
        # Odd sign amsas map to Leo, Cancer respectively & even
        # signs amsas map to Cancer, Leo
        index_sign_map = [5, 4, 4, 5] * 6
    elif type == 'Parivṛtti':
        # Also called Parivṛtti-dvayam. First half of Aries to Ar, second 
        # half to Ta. First half of Taurus to Ge, second half to Cn. Thus, 
        # after Virgo will map to Aq & Pi, Libra will begin the second
        # cycle mapping to Ar & Ta. The second cycle will end with Pisces
        # mapping to Aq & Pi.
        index_sign_map = list(range(1, 13, 1)) * 2
    elif type == 'Uma Shambhu':
        # This is the Uma-Shambhu mapping as stated by PVR. 
        # This is a variation of the Parivṛtti mapping as above, 
        # except that for even signs, the mapping is reversed. So, instead of 
        # Taurus mapping to Ge & Cn, it would map to Cn & Ge. Similarly, 
        # Virgo would map to Pi & Aq. Odd signs are the same as regular 
        # Parivṛtti.
        index_sign_map = [
            n for i in range(1, 12, 4) for n in (i, i + 1, i + 3, i + 2)
        ] * 2
    elif type == 'Kāśīnāth':
        # All signs are calssified as day/night signs. The classification is
        # (from Aries to Pisces) N, N, N, N, D, D, D, D, N, N, D, D. All 5 
        # grahas rule one day and one night sign. 
        # Next, for odd signs, the first half is Sun Hora (i.e. maps to day
        # sign) and the second half is Moon hora (i.e. maps to night sign). 
        # For even signs, it is the reverse.
        # The sign the index maps to is the day/night sign of the lord of 
        # the natal sign. e.g. Jupiter 25°Ta16' maps to Libra as Libra is 
        # the day sign of the lord of Taurus (Venus) and 25°16' is in the 
        # second half of the even sign of Taurus (i.e. Sun Hora). Similarly,
        # Mars at 18°Sa53' maps to Moon Hora, which maps to night sign of 
        # Jupiter, i.e. Sagittarius. 
        # Leo & Cancer are treated specially as "ruled by the same planet".
        # The below mapping is hand constructed on the above rules.
        index_sign_map = [
            8, 1,   # Ar (Odd, Night): Sun(D)=Sc, Moon(N)=Ar
            2, 7,   # Ta (Even, Night): Moon(N)=Ta, Sun(D)=Li
            6, 3,   # Ge (Odd, Night): Sun(D)=Vi, Moon(N)=Ge
            4, 5,   # Cn (Even, Night): Moon(N)=Cn, Sun(D)=Le
            5, 4,   # Le (Odd, Day): Sun(D)=Le, Moon(N)=Cn
            3, 6,   # Vi (Even, Day): Moon(N)=Ge, Sun(D)=Vi
            7, 2,   # Li (Odd, Day): Sun(D)=Li, Moon(N)=Ta
            1, 8,   # Sc (Even, Day): Moon(N)=Ar, Sun(D)=Sc
            12, 9,  # Sa (Odd, Night): Sun(D)=Pi, Moon(N)=Sa
            10, 11, # Ca (Even, Night): Moon(N)=Ca, Sun(D)=Aq
            11, 10, # Aq (Odd, Day): Sun(D)=Aq, Moon(N)=Ca
            9, 12   # Pi (Even, Day): Moon(N)=Sa, Sun(D)=Pi
        ]
    elif type == 'Jagannāth':
        # TODO: Logic doesn't match with JHora's results. What's wrong?
        # Using the same day/night classification as Kāśīnāth, the mapping 
        # is 1/7. i.e. if odd & day sign, Sun hora mapped to itself, Moon 
        # hora mapped to 7th from it. If odd & night sign, Sun hora mapped 
        # to 7th from & Moon hora mapped to itself. If even & day: 7/1, 
        # if even & night: 1/7
        index_sign_map = [
            7, 1,  # Ar (Odd, Night): Sun(D)=Sc, Moon(N)=Ar
            2, 8,  # Ta (Even, Night): Moon(N)=Ta, Sun(D)=Li
            9, 3,  # Ge (Odd, Night): Sun(D)=Vi, Moon(N)=Ge
            4, 10, # Cn (Even, Night): Moon(N)=Cn, Sun(D)=Le
            5, 11, # Le (Odd, Day): Sun(D)=Le, Moon(N)=Cn
            12, 6, # Vi (Even, Day): Moon(N)=Ge, Sun(D)=Vi
            7, 1,  # Li (Odd, Day): Sun(D)=Li, Moon(N)=Ta
            2, 8,  # Sc (Even, Day): Moon(N)=Ar, Sun(D)=Sc
            3, 9,  # Sa (Odd, Night): Sun(D)=Pi, Moon(N)=Sa
            10, 4, # Ca (Even, Night): Moon(N)=Ca, Sun(D)=Aq
            11, 5, # Aq (Odd, Day): Sun(D)=Aq, Moon(N)=Cn
            6, 12  # Pi (Even, Day): Moon(N)=Sa, Sun(D)=Pi
        ]
    elif type == 'Samasaptaka':
        # For all rasis, irrespective of odd/even, the first half is mapped 
        # to the rasi itself and the second is mapped to the 7th from itself
        index_sign_map = [
            ((n - 1) % 12) + 1 for i in range(1, 13, 1) for n in (i, i + 6)
        ]
    elif type == 'Maṇḍūka':
        # For all rasis, first half maps to itself, the second half maps to 
        # 3rd from itself
        index_sign_map = [
            ((n - 1) % 12) + 1 for i in range(1, 13, 1) for n in (i, i + 2)
        ]
    elif type == 'Lābha maṇḍūka':
        # For all rasis, first half maps to itself, the second half maps to 
        # 11th from itself
        index_sign_map = [
            ((n - 1) % 12) + 1 for i in range(1, 13, 1) for n in (i, i + 10)
        ]
    p['Sign'] = p['Hora index'].apply(lambda x: index_sign_map[x])
    # Pull in info about amsā devata
    p['Amsā Devatā'] = p.apply(
        lambda df: (
            amsa_devata_mapping[df['Amsā'] + 1] if df['Rasi sign'] % 2 != 0
            else amsa_devata_mapping[d - df['Amsā']]
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
