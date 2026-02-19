import misc_functions as mf
import chart.chart as crt
from chart.chart_minimal import chart_minimal
from constants import rasis, rnp
from divisionals.divisional_helpers import add_house

amsa_devata_mapping = {
    1: 'Deva', 2: 'Nara', 3: 'Rākṣasa', 
    4: 'Deva', 5: 'Nara', 6: 'Rākṣasa', 
    7: 'Deva', 8: 'Nara', 9: 'Rākṣasa'
}

def d9(birth_crt:crt.chart) -> chart_minimal:
    '''
    Compute the navamsa (D-9) of a birth chart
    Args:
        birth_crt (chart): The natal (D-1) chart for which the navamsa need to be computed.
    Returns:
        A chart_minimal object with the navamsa placements including degrees
    '''
    p = birth_crt.rasi.placements
    # Which amsa is a planet in? (i.e. 0-8)
    p['Amsā'] = p['Lon30'].apply(lambda x: int(x // (30/9)))
    # How much has the planet progressed in the amsā?
    p['Lon30'] = p['Lon30'].apply(lambda x: 30*((x/(30/9))%1))
    # Pull in info about amsā devata
    p['Amsā Devatā'] = p['Amsā'].apply(lambda x: amsa_devata_mapping[x + 1])
    # Find element of rasi containing the graha. This is used to find the 
    # starting sign to count from to arrive at the navamsa sign
    def element_mapping(natal_rasi, rasis_df = rasis):
        '''
        Map a rasi to the starting rasi in the navamsa. For internal use only
        Fire signs map to Aries, Earth to Capricorn, Air to Libra and Water to Cancer
        '''
        # Mapping of rasis to elements
        r = rasis.set_index('Rasi')
        r = r.to_dict(orient = 'index')
        e = r[natal_rasi]['Element']
        # Returns the index of the intended rasis (i.e. Cancer = 3)
        if e == 'Fire':
            return 0
        elif e == 'Earth':
            return 9
        elif e == 'Air':
            return 6
        elif e == 'Water':
            return 3
    # Offset navamsa starting house by divisional progression
    def d9_progression(natal_rasi, progression):
        '''
        Compute the navamsa, given the natal rasi and the progression
        '''
        start_rasi = element_mapping(natal_rasi = natal_rasi)
        navamsa_rasi = int((start_rasi + progression) % 12 + 1)
        return navamsa_rasi
    p['Sign'] = p.apply(lambda x: d9_progression(x.Rashi, x['Amsā']), axis = 1)
    p['Rashi'] = p['Sign'].apply(lambda x: list(rasis['Rasi'])[x - 1])
    p['Lon°'] = p['Lon30'].apply(lambda x: mf.dms(degrees = x))
    p['Lon'] = p.apply(lambda x: x['Lon30'] + 30 * x['Sign'] - 30, axis = 1)
    p = add_house(p = p)
    add_cols = ['Rashi', 'Nakshatra', 'Nakshatra lord', 'Pada']
    p = mf.add_non_equi_col(
        p1 = p,
        p2 = rnp,
        p1col = 'Lon',
        p2col_range = 'Degrees',
        p2col_get = add_cols
    )
    p = p[[
        'Date', 'Time', 'tz', 'Graha', 'Lon', 'Lon°', 'Lon30', 'Amsā', 
        'Amsā Devatā', 'Sign', 'Bhava', 'Rashi', 'Nakshatra', 
        'Nakshatra lord', 'Pada', 'Speed'
    ]]
    out = chart_minimal(
        placements = p, 
        display_cols = [
            'Graha', 'Lon°', 'Amsā Devatā', 'Nakshatra', 
            'Nakshatra lord', 'Pada'
        ]
    )
    return out
