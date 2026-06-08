from subprocess import run
import pandas as pd
from io import StringIO

def read_stdout(
    cmd: str, reader: str, sep: str, col_names: list[str]
) -> pd.DataFrame:
    '''
    Run a shell command, read the stdout and return it as a pandas dataframe.

    Args:
        cmd (str): a shell command to run. Since this is not exposed to 
            users, this should be fine.
        reader (str): One of 'table' or 'csv' depending on stdout
        sep (str): Column separator to be used to read contents of stdout
        col_names (list[str]): A list of column names to assign to the 
            resulting DataFrame.

    Returns:
        pd.DataFrame: A pandas dataframe with the contents of stdout
    '''
    cmd_run = run(
        cmd, capture_output = True, text = True, check = True, shell = False
    )
    reader_map = {
        'table': pd.read_table,
        'csv': pd.read_csv,
        'fixed_width': pd.read_fwf
    }
    if reader not in reader_map:
        raise ValueError(f'Unsupported reader type: {reader}')
    return reader_map[reader](
        StringIO(cmd_run.stdout),
        sep = sep,
        names = col_names,
        index_col = False
    )
