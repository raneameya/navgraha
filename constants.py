import pandas as pd
from fractions import Fraction

rnp=pd.read_csv('rnp.csv')
rnp['Start']=rnp['Start'].apply(lambda x: Fraction(x).limit_denominator())
rnp['End']=rnp['End'].apply(lambda x: Fraction(x).limit_denominator())
