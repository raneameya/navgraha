import subprocess as sp
import pandas as pd
import os

def read_stdout(cmd, reader, sep, col_names):
    tt = sp.run(cmd, stdout=sp.PIPE, shell=True, universal_newlines=True)
    with open('out.txt', 'w') as output:
        output.write(tt.stdout)
    match reader:
        case 'table':
            p = pd.read_table(
                filepath_or_buffer='out.txt', sep=sep, 
                names = col_names, index_col=False   
            )
        case 'csv':
            p = pd.read_csv(
                filepath_or_buffer='out.txt', sep=sep, names=col_names, 
                index_col=False             
            )
    os.remove('out.txt')
    return p

