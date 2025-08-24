from subprocess import run
import pandas as pd
from io import StringIO

def read_stdout(cmd, reader, sep, col_names):
    tt = run(
        args = cmd, capture_output = True, text = True, shell = True
    )
    match reader:
        case 'table':
            p = pd.read_table(
                filepath_or_buffer = StringIO(tt.stdout), sep = sep, 
                names = col_names, index_col = False   
            )
        case 'csv':
            p = pd.read_csv(
                filepath_or_buffer = StringIO(tt.stdout), sep = sep, 
                names = col_names, index_col = False             
            )
    return p

