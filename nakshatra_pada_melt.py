import pandas as pd
import io as io
from fractions import Fraction as fr

# Read rashi nakshtra pada from text data. This is copied from the internet 
# and is wrong in the rashi allocation. The rashi allocation is overwritten 
# later
txt_data = '''Nakshatra	Pada-1	Pada-2	Pada-3	Pada-4
Ashwini	Aries	Taurus	Gemini	Cancer
Bharani	Leo	Virgo	Libra	Scorpio
Krittika	Sagittarius	Capricorn	Aquarius	Pisces
Rohini	Aries	Taurus	Gemini	Cancer
Mrigsira	Leo	Virgo	Libra	Scorpio
Ardra	Sagittarius	Capricorn	Aquarius	Pisces
Punarvasu	Aries	Taurus	Gemini	Cancer
Pushya	Leo	Virgo	Libra	Scorpio
Ashlesha	Sagittarius	Capricorn	Aquarius	Pisces
Magha	Aries	Taurus	Gemini	Cancer
Purva Phalguni	Leo	Virgo	Libra	Scorpio
Uttar Phalguni	Sagittarius	Capricorn	Aquarius	Pisces
Hasta	Aries	Taurus	Gemini	Cancer
Chitra	Leo	Virgo	Libra	Scorpio
Swati	Sagittarius	Capricorn	Aquarius	Pisces
Vishakha	Aries	Taurus	Gemini	Cancer
Anuradha	Leo	Virgo	Libra	Scorpio
Jyeshtha	Sagittarius	Capricorn	Aquarius	Pisces
Moola	Aries	Taurus	Gemini	Cancer
Purva Ashada	Leo	Virgo	Libra	Scorpio
Uttar Ashada	Sagittarius	Capricorn	Aquarius	Pisces
Shravan	Aries	Taurus	Gemini	Cancer
Dhanistha	Leo	Virgo	Libra	Scorpio
Satabhisha	Sagittarius	Capricorn	Aquarius	Pisces
Purva Bhadrapada	Aries	Taurus	Gemini	Cancer
Uttar Bhadrapada	Leo	Virgo	Libra	Scorpio
Revati	Sagittarius	Capricorn	Aquarius	Pisces'''
p = pd.read_csv(io.StringIO(txt_data), sep='\t')

# Source: https://www.selfrealisation.net/UK/VedicAstrology/pada.htm
snippet = [
    'Tendency to use other\'s wealth', 'Childish in acts', 'Fortunate', 
    'Enjoys pleasures; longlived', 'Sacrificial in disposition', 
    'Rich and happy', 'Inflicting suffering ', 'Incurs poverty', 
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

# Melt pada columns into one column to have 108 rows, each corresponding to
# a pada/navamsa
p = pd.melt(frame=p, id_vars=['Nakshatra'],var_name='Pada',value_name='Rashi')
p['Pada']=p['Pada'].str.replace(pat='ada-', repl='')

# Create constants for nakshatras & rashis
nakshatras=p.iloc[
    0:27, p.columns.get_indexer(['Nakshatra'])
]['Nakshatra'].to_list()
rashis=[
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 
    'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

# Vimsottari rulers and respective duration in years
vimsottari=pd.DataFrame({
    'Lords':[
        'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 
        'Saturn', 'Mercury'
    ], 
    'Duration':[x/4 for x in [7, 20, 6, 10, 7, 18, 16, 19, 17]]
})

# Expand out vimsottari table, first each row repeated 4 times and then 
# appended to itself two more times to create the 108 row table we need
vimsottari=vimsottari.loc[vimsottari.index.repeat(4)].reset_index(drop=True)
vimsottari=pd.concat([vimsottari] * 3, ignore_index=True)

# Redefine rashis & nakshatras as ordered categorical variables
# Rashis can only be appended after sorting by nakshatra & pada
p['Nakshatra']=p['Nakshatra'].astype(pd.api.types.CategoricalDtype(
    categories=nakshatras, ordered=True
))
p.sort_values(by=['Nakshatra', 'Pada'], inplace=True, ignore_index=True)
p['Rashi']=pd.Series([r for r in rashis for _ in range(9)]).astype(
    pd.api.types.CategoricalDtype(categories=rashis, ordered=True)
)

# Append vimsottari info
p[['Nakshatra lord', 'Vimshottari dasa (yrs)']]=vimsottari

# Append snippet info from Yavana Jataka as mentioned in the 
# Hora Ratnam of Bala Bhadra. 
p['Snippet']=pd.Series(data=snippet)

# Define start & end degrees for each navamsa/pada
p[['Start', 'End']]=pd.DataFrame({
    'Start':[fr(i, 3) for i in range(1080) if i%10 == 0],
    'End':[fr(i+10, 3) for i in range(1080) if i%10 == 0]
})

# Reorder columns
p=p[[
    'Rashi', 'Nakshatra', 'Nakshatra lord', 'Vimshottari dasa (yrs)', 
    'Pada', 'Start', 'End', 'Snippet'
]]

# Write out
p.to_csv('rnp_py.csv', index=False)
