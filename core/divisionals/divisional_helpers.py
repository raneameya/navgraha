from datetime import datetime
from zoneinfo import ZoneInfo

def add_house(p):
    p['Sign'] = p['Lon'].apply(lambda x: int(divmod(x, 30)[0]+1))
    lagna_rashi = p.loc[p['Graha']=='Lagna', 'Sign']
    p['Bhava'] = p['Sign'].apply(lambda x: ((x+(12-lagna_rashi))%12)+1)
    return p
