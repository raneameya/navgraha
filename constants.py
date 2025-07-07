import pandas as pd, pickle as pl

with open('lut.pickle', 'rb') as handle:
    lut = pl.load(handle)

# Read in mapping table for rashi-nakshatra-pada (i.e. 108 rows)
rnp=lut['Navamsa']

# Create aggregated table for only nakshatras
nakshatra=lut['Nakshatra']

# Read in list of ayanamsas and their swetest arguments. Used to expose 
# list of available ayanmsas to user
ayanamsas=pd.read_csv('ayanamsa_list.csv', index_col='Argument')
