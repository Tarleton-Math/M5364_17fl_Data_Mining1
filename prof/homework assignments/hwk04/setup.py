import numpy as np
import pandas as pd
import sklearn as skl
import sys
import itertools as it
import math
from copy import copy
import datetime
import os

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
from ipywidgets import interact

plt.style.use("fivethirtyeight")
plt.rc("figure", figsize=(5,7))
sns.set_palette('deep')

import IPython.display as ipd
digits = 3
pd.options.display.chop_threshold = 10**-(digits+1)
pd.options.display.float_format = lambda x: '{0:.{1}f}'.format(x,digits)
pd.options.display.show_dimensions = True
def display(X, rows=None):
    if(rows == 'all'):
        rows = 2000
    elif(type(rows) is int):
        rows *= 2
    else:
        rows = 10

    pd.set_option('display.max_rows', rows)
    if isinstance(X, pd.Series) or (isinstance(X, np.ndarray) and X.ndim <=2):
        ipd.display(pd.DataFrame(X))
    else:
        ipd.display(X)
    pd.reset_option('display.max_rows')


def tile_rows(v,n):
    return np.tile(v,(n,1))

def tile_cols(v,n):
    return np.tile(v[:,np.newaxis],(1,n))

def margins(df):
    df = pd.DataFrame(df)
    col_sums = df.sum(axis=0)
    df.loc['TOTAL'] = col_sums
    row_sums = df.sum(axis=1)
    df['TOTAL'] = row_sums
    return df

def get_summary_stats(v):    
    ss = pd.DataFrame(v).describe().T
    ss['SE'] = ss['std'] / np.sqrt(ss['count'])
    return ss