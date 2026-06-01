import re

import pandas as pd

from core.chart.chart import chart

def read_jh_lons(paths: list[str]) -> pd.DataFrame:
    '''
    Reads a number of text files containing all divisional lons and returns
    a deduped flat pandas df.

    Args:
        paths (list[str]): A list of filepaths to files containing the
            clipboard data from the "All Divisional Longitudes" section
            of JHora. Multiple such files can be required because you need
            to cycle through the various varga subtypes for each varga in
            JHora (D-2 & D-3 have many subtypes each)
    Returns:
        pd.DataFrame: A "molten" dataframe with Varga, Graha & Lon. Each
            varga is included only once even though they may be included
            more than once in the input files.
    '''
    df_list = [pd.read_fwf('tests/jh_data/' + p) for p in paths]
    df_list = [
        df.melt(id_vars = 'Body', var_name = 'VargaJH', value_name = 'Lon') 
        for df in df_list
    ]
    df = pd.concat(df_list, ignore_index = True).drop_duplicates()
    return df

def format_jh_lon(x: str) -> float:
    '''
    Converts JHora longitudes of the type "27Cp50" to a longitude in the
    zodiac wheel. These longitudes are between 0-360 and do not take into
    account houses.

    Args:
        x (str): A str of the type DegSignMin (e.g. 27Cp50)
    Returns:
        lon: The longitude (float) corresponding to `x` (e.g. 27Cp50 = 297.83)
    '''
    sign_lon_map = {
        'Ar':0, 'Ta':30, 'Ge':60, 'Cn':90, 'Le':120, 'Vi':150, 
        'Li':180, 'Sc':210, 'Sg':240, 'Cp':270, 'Aq':300, 'Pi':330
    }
    match = re.match(r"(\d+)([A-Za-z]{2})(\d+)", x.strip())
    if match:
        degrees = int(match.group(1))
        sign = match.group(2)
        arcminutes = int(match.group(3))
    lon = sign_lon_map[sign] + degrees + (arcminutes / 60)
    return lon

def process_jh_lons(paths: list[str]) -> pd.DataFrame:
    '''
    A wrapper function to read raw JHora lons, process the longitudes to
    float, map graha names to match the names in the app and output a
    clean df for testing.

    Args:
        path (list[str]): A list of filepaths to files to pass to
            `read_jh_lons`.
    Returns:
        pd.DataFrame: A DataFrame with Varga, Graha & Lon. Typically used
            to provide a reference set of longitudes to compare with.
    '''
    df = read_jh_lons(paths = paths)
    df['Lon'] = df['Lon'].map(format_jh_lon)
    # Map graha names to names in app
    graha_map = {
        'Lagna': 'Lagna', 'Surya': 'Sūrya', 'Chandra': 'Candra', 
        'Budha': 'Budha', 'Sukra': 'Śukra', 'Mangala': 'Maṅgala', 
        'Guru': 'Guru', 'Sani': 'Śani', 'Rahu': 'Rāhu', 'Ketu': 'Ketu'
    }
    df['Graha'] = df['Body'].map(graha_map).fillna(df['Body'])
    return df[['VargaJH', 'Graha', 'Lon']]

def chart_vargas(crt: chart) -> pd.DataFrame:
    '''
    Stack all the divisional chart tables of a chart object and return
    a minimal pandas df with Varga, Graha & Lon.

    Args:
        crt (chart): A chart object.
    Returns:
        pd.DataFrame: A DataFrame with Varga, Graha & Lon. Easily usable
            with testing to compare with JHora results
    '''
    varga_map = pd.read_table(
        filepath_or_buffer = 'tests/varga_mapping.txt', header = None, 
        names = ['VargaJH', 'varga_id', 'Varga']
    )
    vargas_dict = {
        v:getattr(crt.divisionals, v).placements 
        for v in varga_map['varga_id']
    }
    vargas = pd.concat(vargas_dict).reset_index(
        names = ['varga_id', 'id']
    ).drop(labels = ['id'], axis = 1)
    vargas = pd.merge(left = vargas, right = varga_map, on = 'varga_id')
    return vargas[['VargaJH', 'Graha', 'Lon']]
