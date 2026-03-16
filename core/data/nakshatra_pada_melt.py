from fractions import Fraction as fr
import pickle as pl

import pandas as pd

from core.misc.fractional_interval import fractional_interval as fi

# Define nakṣatra level info
nakshatras = {
    'Nakṣatra': [
        'Aśvinī', 'Bharaṇī', 'Kṛttikā', 'Rohiṇī', 'Mṛgaśīrṣā', 'Ārdrā', 
        'Punarvasu', 'Puṣya', 'Āśleṣā', 'Maghā', 'Pūrva Phalgunī', 
        'Uttara Phalgunī', 'Hasta', 'Citrā', 'Svāti', 'Viśākhā', 'Anurādhā', 
        'Jyeṣṭhā', 'Mūla', 'Pūrvāṣāḍhā', 'Uttarāṣāḍhā', 'Śravaṇa', 'Dhaniṣṭhā', 
        'Śatabhiṣaj', 'Pūrva Bhādrapadā', 'Uttara Bhādrapadā', 'Revatī'
    ],
    'Graha devatā': [
        'Ketu', 'Śukra', 'Sūrya', 'Candra', 
        'Maṅgala', 'Rāhu', 'Guru', 'Śani', 'Budha'
    ] * 3,
    'Planetary ruler': [
        'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 
        'Rahu', 'Jupiter', 'Saturn', 'Mercury'
    ] * 3,
    'Graha unicode': [
        '\u260B', '\u2640', '\u2609', '\u263E', '\u2642', 
        '\u260A', '\u2643', '\u2644', '\u263F'
    ] * 3,
    'Viṃśottarī daśā length': [
        x/4 for x in [7, 20, 6, 10, 7, 18, 16, 19, 17]
    ] * 3
}
nakshatras = pd.DataFrame(nakshatras)
nakshatras['Nakṣatra'] = nakshatras['Nakṣatra'].astype(
    pd.api.types.CategoricalDtype(
        categories = nakshatras['Nakṣatra'].to_list()[0:27], ordered = True
    )
)

# Define padas
padas = pd.DataFrame(['P1', 'P2', 'P3', 'P4'], columns = ['Pada'])

# Create navamsa table (27 * 4 = 108 rows)
navamsa = pd.merge(nakshatras, padas, how = 'cross')

# Define rāśi level info
rasis_dict = {
    'Rāśi': [
        'Meṣa', 'Vṛṣabha', 'Mithuna', 'Karka', 'Siṃha', 'Kanyā', 
        'Tulā', 'Vṛścika', 'Dhanu', 'Makara', 'Kumbha', 'Mīna'
    ],
    'Zodiac sign': [
        'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
        'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
    ],
    'Graha devatā': [
        'Maṅgala', 'Śukra', 'Budha', 'Candra', 'Sūrya', 'Budha', 
        'Śukra', 'Maṅgala', 'Guru', 'Śani', 'Śani', 'Guru'
    ],
    'Planetary ruler': [
        'Mars', 'Venus', 'Mercury', 'Moon', 'Sun', 'Mercury', 
        'Venus', 'Mars', 'Jupiter', 'Saturn', 'Saturn', 'Jupiter'
    ],
    'Graha unicode': [
        '\u2642', '\u2640', '\u263F', '\u263E', '\u2609', '\u263F', 
        '\u2640', '\u2642', '\u2643', '\u2644', '\u2644', '\u2643'
    ],
    'Rāśi unicode': [
        '\u2648', '\u2649', '\u264A', '\u264B', '\u264C', '\u264D', 
        '\u264E', '\u264F', '\u2650', '\u2651', '\u2652', '\u2653'
    ],
    'Element': ['Fire', 'Earth', 'Air', 'Water'] * 3, 
    'Modality': ['Chara', 'Sthira', 'Dvisvabhāva'] * 4, 
    'Gender': ['Male', 'Female'] * 6, 
    'Nature': [
        'Krūra', 'Saumya', 'Miśra', 'Saumya', 'Krūra', 'Miśra', 
        'Saumya', 'Krūra', 'Saumya', 'Krūra', 'Krūra', 'Saumya'
    ], 
    'Direction': ['East', 'South', 'West', 'North'] * 3,
    'Varṇa': ['Kṣatriya', 'Vaiśya', 'Śūdra', 'Brahmin'] * 3
}
rasis = pd.DataFrame({
    k: [x for x in v for _ in range(9)] for k, v in rasis_dict.items()
})
rasis['Rāśi'] = rasis['Rāśi'].astype(
    pd.api.types.CategoricalDtype(
        categories = rasis_dict['Rāśi'], ordered = True
    )
)
add_cols = ['Rāśi', 'Zodiac sign', 'Rāśi unicode']
navamsa[add_cols] = rasis[add_cols]

# Define start & end degrees for each navamsa/pada
navamsa[['Start', 'End']] = pd.DataFrame({
    'Start':[fr(i, 3) for i in range(1080) if i%10 == 0],
    'End':[fr(i+10, 3) for i in range(1080) if i%10 == 0]
})

# Create fractional interval column
navamsa['Degrees'] = pd.Series([
    fi(left=fr(i, 3), right = fr(i+10, 3), closed = 'left') 
    for i in range(1080) if i%10 == 0
])

# Indicate Pushkara amsas
pushkara_amsas = [
    # Aries [20°0'0.0, 23°20'0.0)
    fi(left = 20, right = fr(70, 3), closed = 'left'),
    # Aries [26°40'0.0, 0°0'0.0)
    fi(left = fr(80, 3), right = 30, closed = 'left'), 
    # Taurus [6°40'0.0, 10°0'0.0)
    fi(left = fr(110, 3), right = 40, closed = 'left'),
    # Taurus [13°20'0.0, 16°40'0.0)
    fi(left = fr(130, 3), right = fr(140, 3), closed = 'left'),
    # Gemini [16°40'0.0, 20°0'0.0)
    fi(left = fr(230, 3), right = 80, closed = 'left'),
    # Gemini [23°20'0.0, 26°40'0.0)
    fi(left = fr(250, 3), right = fr(260, 3), closed = 'left'), 
    # Cancer [0°0'0.0, 3°20'0.0)
    fi(left = 90, right = fr(280, 3), closed = 'left'),
    # Cancer [6°40'0.0, 10°0'0.0)
    fi(left = fr(290, 3), right = 100, closed = 'left')
]
# Add 120° to cover other 8 signs symmetrically
pushkara_amsas = [
    fi(left = (x.left + 120 * i), right = (x.right + 120 * i), closed = 'left') 
    for i in range(3) for x in pushkara_amsas
]
# Add Pushkara column
navamsa['Puṣkara'] = navamsa['Degrees'].apply(
    lambda d: 'Yes' if d in pushkara_amsas else 'No'
)

# Source: https://www.selfrealisation.net/UK/VedicAstrology/pada.htm
# Supposedly from Yavana Jataka as mentioned in Hora Ratnam of Bala Bhadra
snippet = [
    'Tendency to use other\'s wealth', 'Childish in acts', 'Fortunate', 
    'Enjoys pleasures; longlived', 'Sacrificial in disposition', 
    'Rich and happy', 'Inflicting suffering', 'Incurs poverty', 
    'Radiant', 'Has knowledge of scriptures', 'Experiences grief', 
    'Enjoys longevity and many sons', 'Highly prosperous', 'Incurs evils', 
    'Timid in disposition', 'Truthful', 'Kingly in status', 
    'Tendency to use other\'s wealth', 'Enjoys pleasures', 
    'Endowed with wealth and grains', 'Spendthrift', 'In the grip of poverty', 
    'Short-lived', 'Tendency to use other\'s wealth', 'Happy', 'Learned', 
    'Weak health', 'Not truthful', 'Long-lived', 
    'Tendency to use other\'s wealth', 'Enjoys pleasures', 'Intelligent', 
    'Childless', 'In servitude', 'Weak health', 'Very prosperous', 
    'No male progeny', 'Male progeny', 'Suffers from dangerous disease', 
    'A scholar', 'Skilful person', 'Righteous', 'Inflicting suffering', 
    'Short-lived', 'Scholar', 'Ruler of the earth', 'Successful ', 
    'Righteous', 'Heroic', 'Learned', 'Weak health', 'Wealthy', 
    'Tendency to use other\'s wealth', 'Artist', 'Truthful', 'Learned', 
    'Tendency to use other\'s wealth', 'Short-lived', 'Charitable', 'King', 
    'Well-versed in justice and policy-making', 'Versed in sciptures', 
    'Learned', 'Endowed with longevity', 'Fierce', 'Charitable', 'Long-lived', 
    'Questionable history', 'Inflicting suffering', 'Enjoys pleasures', 
    'Quite intelligent', 'Male issues', 'Enjoys pleasures', 
    'Sacrificial disposition', 'Endowed with good friends', 'Lordly', 
    'Excellent person', 'Kingly', 'Eloquent in speech', 'Wealthy', 'Lordly', 
    'Inimical (even) to friends', 'Honourable', 'Religious', 
    'Highly honourable', 'Endowed with virtues', 'Scholar', 'Charitable', 
    'Enjoys longevity', 'Scholar', 'Timid in disposition', 
    'Under the influence of a great woman', 'Eloquent in speech', 
    'Wealthy', 'Endowed with happiness', 'Male offspring', 'Valorous', 
    'Tendency to use other\'s wealth', 'Possesses great intelligence', 
    'Enjoys pleasures', 'Kingly', 'Tendency to use other\'s wealth', 
    'Male issues', 'Happy', 'Spiritual wisdom', 
    'Tendency to use other\'s wealth', 'Winner in battles', 'Incurring grief'
]

navamsa['Snippet'] = pd.Series(snippet)

col_order = [
    'Rāśi', 'Nakṣatra', 'Graha devatā', 'Viṃśottarī daśā length', 
    'Pada', 'Start', 'End', 'Degrees', 'Puṣkara', 'Snippet'
]
rasis = pd.DataFrame(rasis_dict)

# Pickle file and save on disk
out = {
    'Navāṁśa': navamsa,
    'Rāśi': rasis
}

with open('core/data/lut.pickle', 'wb') as handle:
    pl.dump(out, handle, protocol = 0)
