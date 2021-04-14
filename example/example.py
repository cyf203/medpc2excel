# -*- coding: utf-8 -*-
"""
Created on Wed Apr 14 19:22:04 2021

@author: yifeng cheng
"""

from medpc2excel.medpc_read import medpc_read

f = 'xxx'

# medpc_read function return two outpus.
# the first one is actual data

# if you don't want export you data into *.xlsx file
data, _ = medpc_read(f,save=False)  

# if you do want a *.xlsx file (default is save)
data, _ = medpc_read(f)  # note that data is a dict-liked data structure

# to access the specific animal data in a specific date in the exmaple
df = data['date']['id'] # df is a pandas dataframe for this animal in this date