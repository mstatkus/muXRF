# -*- coding: utf-8 -*-
"""
Created on Sat Jul 17 15:02:45 2021

@author: Михаил
"""
#%% init
import pandas as pd
import numpy as np


xls_files = ['KPV-2021-07-13-NS.xls',
             'KPV-2021-07-13-2-NS.xls',
             'KPV-2021-07-14-NS.xls',
             'KPV-2021-07-16-NS.xls',
             'KPV-2021-07-20-NS.xls']

filter_elements = ['Cu','Zn','Pb','Rb','Sr','Y','Zr']
drop_elements = ['O']

def clean_xls_data(df):
    sample_name_regex = "[A-Z]{3}-(?P<id>\d{1,3})(?P<filter>-f)?"
    
    ids = df['Spectrum'].str.extract(sample_name_regex,
                                     expand = True)
    
    ids['filter'] = ids['filter'].str.replace('-f','1')
    ids['filter'] = ids['filter'].fillna(value=0)
    
    ids['filter'] = ids['filter'].astype('bool')
    
    ids['id'] = ids['id'].astype('int')
    
    df = ids.join(df)
    df.set_index(['id','filter','Spectrum'],
             inplace=True)
    
    df = df.drop(columns=drop_elements)
    
    return df

def read_and_clean_xls(xls_file):
    df = pd.read_excel(xls_file,
                       header = 0,
                       skiprows = 7,
                       skipfooter = 5)
    df = clean_xls_data(df)
    
    return df
  
def lognorm(df,
            norm_by = 'Fe',
            replace_zeros = True,
            replace_with = 1):
    
    if replace_zeros:
        df = df.replace(to_replace=0, value=replace_with)
        
    df_norm = df.divide(df[norm_by],axis=0)
    df_norm = df_norm.apply(np.log10)
    df_norm = df_norm.apply(np.negative)
    
    return df_norm
    
def process_filter_data(df, filter_elements,drop_fe=True):
    
    
    # split to filter and no-filter dataframes
    df_nofilter=df.query("filter==False")
    df_filter = df.query("filter==True")
    
    # keep these elements in filter=True rows,
    # drop them from filter=False rows
    
    
    df_nofilter=df_nofilter.drop(columns = filter_elements)
    
    df_filter = df_filter[filter_elements]
    
    # drop 'filter' and 'Spectrum' from multiindex
    df_filter.reset_index(level=['filter','Spectrum'],
                          drop=True, inplace = True)
    
    df_nofilter.reset_index(level=['filter','Spectrum'],
                            drop=True, inplace = True)
    
    # join dframes and drop fe column
    df1 = df_nofilter.join(df_filter)
    if drop_fe:
        df1.drop(columns=['Fe'],inplace=True)
    
    return df1


def read_xls_list(xls_files):
    # read and clean data
    dfs = []
    for f in xls_files:
        df = read_and_clean_xls(f)
        dfs.append(df)
    # concatenate
    df = pd.concat(dfs)
    return df


#%% lognorm and process filtered

df = read_xls_list(xls_files)

df_lognorm = lognorm(df,
                     norm_by = 'Fe',
                     replace_zeros = True,
                     replace_with = 1)

df_filtered = process_filter_data(df_lognorm, filter_elements)
df_filtered.sort_index(inplace=True)

df_filtered.to_excel('KPV_lognorm.xlsx')

dfp = process_filter_data(df,filter_elements,drop_fe=False)
dfp.sort_index(inplace=True)
dfp.to_excel('KPV_intensity.xlsx')
