import glob
import csv
import pandas as pd

def get_pep_ccl():
    cola = []
    pepsi = []

    filelist = glob.glob('data/asx/*.csv')
    for infile in sorted(filelist):
        file = open(infile, "rU")
        reader = csv.reader(file, delimiter=',')
        for column in reader:
            if column[0] == 'CCL.AX':
                cola.append(float(column[-2]))
        file.close()

    filelist = glob.glob('data/nasdaq/*.csv')
    for infile in sorted(filelist):
        file = open(infile, "rU")
        reader = csv.reader(file, delimiter=',')
        for column in reader:
            if column[0] == 'PEP':
                pepsi.append(float(column[-2]))
        file.close()

    return pd.Series(pepsi[-500:], name='Prices A'), pd.Series(cola[-500:], name='Prices B')
    # return pd.Series(pepsi[-500:], name=''), pd.Series(cola[-500:])
