import pandas as pd
from fractions import Fraction

# Read in mapping table for rashi-nakshatra-pada
rnp=pd.read_csv('rnp.csv')
rnp['Start']=rnp['Start'].apply(lambda x: Fraction(x).limit_denominator())
rnp['End']=rnp['End'].apply(lambda x: Fraction(x).limit_denominator())

# Read in list of ayanamsas and their swetest arguments
ayanamsas=pd.read_csv('ayanamsa_list.csv', index_col='Argument')
