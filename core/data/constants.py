import pickle as pl # loading pickle file

with open('core/data/lut.pickle', 'rb') as handle:
    lut = pl.load(handle)

# Read in mapping table for rashi-nakshatra-pada (i.e. 108 rows)
rnp = lut['Navāṁśa']

# Table of rasis with attributes
rasis = lut['Rāśi']

# Read in list of ayanamsas and their swetest arguments. Used to expose 
# list of available ayanmsas to user
ayanamsa_dict = {
    'Fagan/Bradley':'00',
    'Lahiri':'1',
    'De Luce':'2',
    'Raman':'3',
    'Usha/Shashi':'4',
    'Krishnamurti':'5',
    'Djwhal Khul':'6',
    'Yukteshwar':'7',
    'J.N. Bhasin':'8',
    'Babylonian/Kugler 1':'9',
    'Babylonian/Kugler 2':'10',
    'Babylonian/Kugler 3':'11',
    'Babylonian/Huber':'12',
    'Babylonian/Eta Piscium':'13',
    'Babylonian/Aldebaran = 15 Tau':'14',
    'Hipparchos':'15',
    'Sassanian':'16',
    'Galact. Center = 0 Sag':'17',
    'J2000':'18',
    'J1900':'19',
    'B1950':'20',
    'Suryasiddhanta':'21',
    'Suryasiddhanta (mean Sun)':'22',
    'Aryabhata':'23',
    'Aryabhata (mean Sun)':'24',
    'SS Revati':'25',
    'SS Citra':'26',
    'True Citra':'27',
    'True Revati':'28',
    'True Pushya (PVRN Rao)':'29',
    'Galactic (Gil Brand)':'30',
    'Galactic Equator (IAU1958)':'31',
    'Galactic Equator':'32',
    'Galactic Equator mid-Mula':'33',
    'Skydram (Mardyks)':'34',
    'True Mula (Chandra Hari)':'35',
    'Dhruva/Gal.Center/Mula (Wilhelm)':'36',
    'Aryabhata 522':'37',
    'Babylonian/Britton':'38',
    'Vedic/Sheoran':'39',
    'Cochrane (Gal.Center = 0 Cap)':'40',
    'Galactic Equator (Fiorenza)':'41',
    'Vettius Valens':'42',
    'Lahiri 1940':'43',
    'Lahiri VP285 (1980)':'44',
    'Krishnamurti VP291':'45',
    'Lahiri ICRC':'46',
    'Tropical':'-1'
}
ayanamsas = [k for k, v in ayanamsa_dict.items()]

yr_len = 365.24219

graha_dict = {
    # 'graha_name': (sweph_ipl, sweph_const)
    # empty string for sweph_const means undefined
    'Lagna': (-2, '', 'La'),
    'Sūrya': (0, 'SE_SUN', 'Sū'),
    'Candra': (1, 'SE_MOON', 'Ch'),
    'Budha': (2, 'SE_MERCURY', 'Me'),
    'Śukra': (3, 'SE_VENUS', 'Ve'),
    'Maṅgala': (4, 'SE_MARS', 'Ma'),
    'Guru': (5, 'SE_JUPITER', 'Gu'),
    'Śani': (6, 'SE_SATURN', 'Sa'),
    'Rāhu': (11, 'SE_TRUE_NODE', 'Rā'),
    'Ketu': (-7, '', 'Ke'),
    'Bhr̥gu Bindu': (-8, '', 'Bb')
}

divisional_choices = {
    'Rāśi (D-1)': {'rasi': 'Rāśi'}, 
    'Navāmśā (D-9)': {'navamsa': 'Navāmśā'}, 
    'Horā (D-2)': {
        'hora_psr': 'Horā (Parashari)', 'hora_us': 'Horā (Uma Shambhu)', 
        'hora_prv': 'Horā (Parivṛtti)', 'hora_ksn': 'Horā (Kāśīnāth)', 
        'hora_ssp': 'Horā (Samasaptaka)', 'hora_mdk': 'Horā (Maṇḍūka)',
        'hora_lmk': 'Horā (Lābha maṇḍūka)'
    }, 
    'Drekkāṇa (D-3)': {
        'drekkana_psr': 'Drekkāṇa (Parashari)',
        'drekkana_us': 'Drekkāṇa (Uma Shambhu)',
        'drekkana_prv': 'Drekkāṇa (Parivṛtti)',
        'drekkana_smn': 'Drekkāṇa (Somanāth)',
        'drekkana_jgn': 'Drekkāṇa (Jagannāth)'
    }, 
    'Caturthāṁśa (D-4)': {
        'chathurtamsa_psr': 'Caturthāṁśa (Parashari)',
        'chathurtamsa_prv': 'Caturthāṁśa (Parivṛtti)'
    },
    'Daśāṃśa (D-10)': {
        'dasamsa_psr': 'Daśāṃśa (Parashari)',
        'dasamsa_rev': 'Daśāṃśa (Parashari reversed)',
        'dasamsa_rev69': 'Daśāṃśa (Parashari reversed (6-9))',
    },
    'Viṃśāṃśa (D-20)': {
        'vimsamsa_psr': 'Viṃśāṃśa (Parashari)',
        'vimsamsa_rev': 'Viṃśāṃśa (Parashari reversed)'
    }, 
    'Triṃśāṃśa (D-30)': {
        'trimsamsa_psr': 'Triṃśāṃśa (Parashari)',
        'trimsamsa_prv': 'Triṃśāṃśa (Parivṛtti)'
    },
    'Khavēdāṃśa (D-40)': {'khavedamsa': 'Khavēdāṃśa'},
    'Ṣaṣṭyāṃśa (D-60)': {
        'sastyamsa_psr': 'Ṣaṣṭyāṃśa (Parashari)',
        'sastyamsa_rev': 'Ṣaṣṭyāṃśa (Parashari reversed)'
    }
}

'''
('SE_ECL_NUT', -1),
('SE_URANUS', 7),
('SE_NEPTUNE', 8),
('SE_PLUTO', 9),
('SE_MEAN_NODE', 10),
('SE_MEAN_APOG', 12),
('SE_OSCU_APOG', 13),
('SE_EARTH', 14),
('SE_CHIRON', 15),
('SE_PHOLUS', 16),
('SE_CERES', 17),
('SE_PALLAS', 18),
('SE_JUNO', 19),
('SE_VESTA', 20),
('SE_INTP_APOG', 21),
('SE_INTP_PERG', 22),
('SE_NPLANETS', 23),
('SE_FICT_OFFSET', 40), #, offset, for, fictitious, objects
('SE_NFICT_ELEM', 15),
('SE_PLMOON_OFFSET', 9000), #, offset, for, planetary, moons
('SE_AST_OFFSET', 10000), #, offset, for, asteroids
#, Hamburger, or, Uranian, "planets", 
('SE_CUPIDO', 40),
('SE_HADES', 41),
('SE_ZEUS', 42),
('SE_KRONOS', 43),
('SE_APOLLON', 44),
('SE_ADMETOS', 45),
('SE_VULKANUS', 46),
('SE_POSEIDON', 47),
#, other, fictitious, bodies
('SE_ISIS', 48),
('SE_NIBIRU', 49),
('SE_HARRINGTON', 50),
('SE_NEPTUNE_LEVERRIER', 51),
('SE_NEPTUNE_ADAMS', 52),
('SE_PLUTO_LOWELL', 53),
('SE_PLUTO_PICKERING', 54)
'''