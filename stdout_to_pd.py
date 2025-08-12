import subprocess as sp
import pandas as pd
import os
from io import StringIO

def read_stdout(cmd, reader, sep, col_names):
    tt = sp.run(
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

