import pickle as pl # loading pickle file

with open('core/data/lut.pickle', 'rb') as handle:
    lut = pl.load(handle)

# Read in mapping table for rashi-nakshatra-pada (i.e. 108 rows)
rnp = lut['Navamsa']

# Create aggregated table for only nakshatras
nakshatra =  lut['Nakshatra']

# Table of rasis with attributes
rasis = lut['Rasi']

# Read in list of ayanamsas and their swetest arguments. Used to expose 
# list of available ayanmsas to user
ayanamsas = [
    'Fagan/Bradley', 'Lahiri', 'De Luce', 'Raman', 'Usha/Shashi', 
    'Krishnamurti', 'Djwhal Khul', 'Yukteshwar', 'J.N. Bhasin', 
    'Babylonian/Kugler 1', 'Babylonian/Kugler 2', 'Babylonian/Kugler 3', 
    'Babylonian/Huber',     'Babylonian/Eta Piscium', 
    'Babylonian/Aldebaran = 15 Tau', 'Hipparchos', 'Sassanian', 
    'Galact. Center = 0 Sag', 'J2000', 'J1900', 'B1950', 'Suryasiddhanta', 
    'Suryasiddhanta (mean Sun)', 'Aryabhata', 'Aryabhata (mean Sun)', 
    'SS Revati', 'SS Citra', 'True Citra', 'True Revati', 
    'True Pushya (PVRN Rao)', 'Galactic (Gil Brand)', 
    'Galactic Equator (IAU1958)', 'Galactic Equator', 
    'Galactic Equator mid-Mula', 'Skydram (Mardyks)', 
    'True Mula (Chandra Hari)', 'Dhruva/Gal.Center/Mula (Wilhelm)', 
    'Aryabhata 522', 'Babylonian/Britton', 'Vedic/Sheoran', 
    'Cochrane (Gal.Center = 0 Cap)', 'Galactic Equator (Fiorenza)', 
    'Vettius Valens', 'Lahiri 1940', 'Lahiri VP285 (1980)', 
    'Krishnamurti VP291', 'Lahiri ICRC', 'Tropical'
]

yr_len = 365.24219
