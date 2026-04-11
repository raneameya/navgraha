# Khavēdāṃśa
from core.misc.misc_functions import add_non_equi_col, dms
import core.chart.chart as crt
from core.chart.chart_minimal import chart_minimal
from core.data.constants import rasis, rnp
from core.divisionals.divisional_helpers import add_house

amsa_devatas = {
    # For amsās greater than 12, the cycle begins again, 
    # even though 40 is not perfectly divisble by 12
    1: ('Vishnu', 'Maintenance', 'Intelligence and Balance'),
    2: ('Chandra', 'Nurturing', 'Domestic Happiness and Intuition'),
    3: ('Marīci', 'Illumination', 'Creative Power and Authority'),
    4: ('Tvaṣṭā', 'Form', 'Craftsmanship and Career Drive'),
    5: ('Dhātā', 'Creation', 'Fulfillment of Desires'),
    6: ('Śiva', 'Dissolution', 'Protection and Transformation'),
    7: ('Ravi', 'Vitality', 'Fame and Inherited Reputation'),
    8: ('Yama', 'Regulation', 'Discipline and Past-Life Results'),
    9: ('Yaksha', 'Resource', 'Material Wealth and Stability'),
    10: ('Gandharva', 'Artistry', 'Aesthetics and Lifestyle'),
    11: ('Kāla', 'Time', 'Cycles and Significant Shifts'),
    12: ('Varuṇa', 'Justice', 'Moral Affairs and Adaptability')
}

def d40(birth_chart) -> chart_minimal:
    '''
    Compute the khavēdāṃśa (D-40) of a birth chart
    Args:
        birth_crt (chart): The base natal (D-1) chart.
    Returns:
        A chart_minimal object with the khavēdāṃśa placements including degrees
    '''
    d = 40
    p = birth_chart.rasi.placements.copy(deep = True)
    # Create a copy of sign in rasi. Used to classify whether graha in 
    # even/odd sign
    p['Natal sign'] = p['Sign']
    # Which amsa is a planet in? (i.e. 0, 1, 2, 3, ..., 39)
    p['Amsā'] = p['Lon30'].apply(lambda x: int(x // (30 / d)))
    # How much has the planet progressed in the amsā?
    p['Lon30'] = p['Lon30'].apply(lambda x: 30 * ((x / (30 / d)) % 1))
    p['Amsā Devatā'] = p['Amsā'].apply(lambda x: amsa_devatas[(x % 12) + 1][0])
    def d40_progression(natal_rasi: int, amsa: int) -> int:
        start_rasi = 1 if natal_rasi % 2 == 1 else 7
        return ((start_rasi - 1 + amsa) % 12) + 1
    p['Sign'] = p.apply(
        lambda df: d40_progression(df['Natal sign'], df['Amsā']), axis = 1
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
