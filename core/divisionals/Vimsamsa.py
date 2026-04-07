# Vimśāṃśa
from core.misc.misc_functions import add_non_equi_col, dms
import core.chart.chart as crt
from core.chart.chart_minimal import chart_minimal
from core.data.constants import rasis, rnp
from core.divisionals.divisional_helpers import add_house

odd_devis = {
    1: ('Kali', 'Transformation', 'Destruction of ego'),
    2: ('Gauri', 'Purity', 'Auspiciousness'),
    3: ('Jaya', 'Victory', 'Success in spiritual battles'),
    4: ('Lakshmi', 'Prosperity', 'Divine grace'),
    5: ('Vijaya', 'Triumph', 'Unconquerable spirit'),
    6: ('Vimala', 'Purity', 'Cleanliness of mind'),
    7: ('Sati', 'Devotion', 'Truthfulness'),
    8: ('Tara', 'Guidance', 'Crossing the ocean of existence'),
    9: ('Jvalamukhi', 'Aura', 'Fiery energy'),
    10: ('Sveta', 'Clarity', 'Luminous wisdom'),
    11: ('Lalita', 'Bliss', 'Divine play/Maya'),
    12: ('Bagalamukhi', 'Stambhana', 'Halting negative forces'),
    13: ('Pratyangira', 'Protection', 'Destroyer of black magic'),
    14: ('Shachi', 'Power', 'Indra\'s queen/Sovereignty'),
    15: ('Raudri', 'Intensity', 'Fierce aspect of Shiva/Shakti'),
    16: ('Bhavani', 'Source of life', 'Nurturing energy'),
    17: ('Varada', 'Giver of boons', 'Compassion'),
    18: ('Jaya', 'Victory', 'Secondary success aspect'),
    19: ('Tripura', 'Transcendent', 'Beyond the three worlds'),
    20: ('Sumukhi', 'Graciousness', 'Bright/Happy face')
}

even_devis = {
    1: ('Daya', 'Mercy', 'Compassion'),
    2: ('Medha', 'Intelligence', 'Memory'),
    3: ('Chinnasirsha', 'Self-sacrifice', 'Severed head/Ego-death'),
    4: ('Pishachini', 'Shadow work', 'Overcoming base desires'),
    5: ('Dhumavati', 'Detachment', 'The widow aspect of Shakti'),
    6: ('Matangi', 'Knowledge', 'Outcast goddess of arts'),
    7: ('Bala', 'Youthful energy', 'Pure potential'),
    8: ('Bhadra', 'Fortunate', 'Gentleness'),
    9: ('Aruna', 'Dawn', 'New beginnings'),
    10: ('Anala', 'Fire', 'Purification'),
    11: ('Pingala', 'Nadi energy', 'Solar channel'),
    12: ('Chuchuka', 'Nurturing', 'Support'),
    13: ('Ghora', 'Terror', 'Fierce discipline'),
    14: ('Varahi', 'Force', 'Boar-headed goddess'),
    15: ('Vaishnavi', 'Sustenance', 'Vishnu\'s energy'),
    16: ('Sita', 'Earth/Purity', 'Rama\'s consort'),
    17: ('Bhuvanesvari', 'Space', 'Queen of the universe'),
    18: ('Bhairavi', 'Fearlessness', 'Fierce protection'),
    19: ('Mangala', 'Auspiciousness', 'Well-being'),
    20: ('Aparajita', 'Invincibility', 'The undefeated')
}

def d20(birth_chart, type: str) -> chart_minimal:
    '''
    Compute the vimśāṃśa (D-20) of a birth chart
    Args:
        birth_crt (chart): The base natal (D-1) chart.
    Returns:
        A chart_minimal object with the vimśāṃśa placements including degrees
    '''
    d = 20
    p = birth_chart.rasi.placements.copy(deep = True)
    # Create a copy of sign in rasi. Used to classify whether graha in 
    # even/odd sign
    p['Natal sign'] = p['Sign']
    # Which amsa is a planet in? (i.e. 0, 1, 2, ... 19)
    p['Amsā'] = p['Lon30'].apply(lambda x: int(x // (30/d)))
    # Pull in info about amsā devata. Reverse pull if graha is in 
    # even sign natally
    p['Amsā Devatā'] = p.apply(
        lambda df: (
            odd_devis[df['Amsā'] + 1][0]
            if df['Natal sign'] % 2 == 1
            else even_devis[df['Amsā']][0]
        ), 
        axis = 1
    )
    # How much has the planet progressed in the amsā?
    if type == 'Traditional Parashari':
        p['Lon30'] = p['Lon30'].apply(lambda x: 30 * ((x / (30 / d)) % 1))
    elif type == 'Parashari reversed':
        p['Lon30'] = p.apply(lambda df: (
                30 * ((df['Lon30'] / (30 / d)) % 1) 
                if df['Natal sign'] % 2 != 0
                else 30 - (30 * ((df['Lon30'] / (30 / d)) % 1))
            ), axis = 1
        )    
    def d20_progression(natal_rasi: int, amsa: int, type: str) -> int:
        start_rasis = [1, 9, 5] # moveable, dual & fixed dharma trikona
        start_rasi = start_rasis[(natal_rasi - 1) % 3]
        if natal_rasi % 2 == 1:
            # For all variations, if natal sign is odd, progression 
            # is forward starting from natal rasi
            return ((start_rasi - 1 + amsa) % 12) + 1
        else:
            # Different variations of progression if natal sign is even
            if type == 'Traditional Parashari':        
                # go forward
                return ((start_rasi - 1 + amsa) % 12) + 1
            elif type == 'Parashari reversed':
                # start from 8th sign from start sign and reverse progression
                return ((start_rasi + 7 - 1 - amsa) % 12) + 1
    p['Sign'] = p.apply(
        lambda df: d20_progression(
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
