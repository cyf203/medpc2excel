# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 11:38:04 2019
Edited on Fri August 9 11:23   2019
          add  __get_data_from_medpc() to read raw MEDPC data
          add __get_data_dict_subjname() to select which read method should be used
Edited on Fri August 23 12:53 2019
          line 53, 55, 162 remove ID parameter
Edited on Fri August 23 15:34 2019
          biricated version. Version 2
Edited on Sat August 24 22:00 2019 
          Remove three functions: __get_data_from_excel, __get_TS_tree, __get_single_eventTS
          Add Function __add_trial_index, get_subj_df
          Features change: 1. can add trial index with tiral reference information provided
                           2. Remove complicated event and response extraction function.
                           3. Purely focused on extract rat data from MedPC file
                           4. This class no longer support reading excel or csv raw file
          Tested! Well!
Edited on Fri Jan 10 12:39 2020
          Revise the code so that it can catch meaningful empty variables (e.g., when animal press 0 or nosepoke 0 time) 
Edited on Fri Jan 10 20:08 2020
          Add the code at line 167 under if this file has existed, then append data to this excel
Edited on Fri Jan 17 11:02 2020
          Revise the saving module at from line 164. It now give user options to replace or not for existing subjects in an existing excel
Edited on Fri Jan 17 11:40 2020
          Remove date_filer variable and related modules
          Revise line 86: adding a type force conversion
          Add a check for variable <trial_ref_df> at line 228
Edited on Fri Jan 17 17:11 2020
          Add the sort method for <common_var> list to fix the bug that cannot get the data from the last variable

Version   1.0
@author: ycheng62
"""

from __future__ import division, print_function

import re
import os
import pandas as pd
import numpy as np
from datetime import datetime

class medpc_read:
    """
    Attributes:
        date
        write
        file
        currentTime
        df_dict
        workingVar_dict
        subj_list
    """
    def __init__ (self, file, rat_id=None, save = True, replace = True):
        '''
        Parameters
        ----------
        file : TYPE
            DESCRIPTION.
        rat_id : TYPE, optional
            DESCRIPTION. The default is None.
        save : TYPE, optional
            DESCRIPTION. The default is True.
        replace : TYPE, optional
            DESCRIPTION. The default is True.

        Returns
        -------
        None.

        '''
        self.date = '19910203'
        self.save = save
        self.replace = replace
        self.file = file
        self.currentTime = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        self.df_dict, self.workingVar_dict = self.__get_data_from_medpc(rat_id)
        self.subj_list = list(self.df_dict.keys())
        print ('Get subjects:', self.subj_list)
    
    #private method
    def __get_data_from_medpc (self, rat_id):
        #load raw file into dict
        alldata_dict = {}
        subject_list= []
        with open(self.file, 'r') as f:
            datasets = f.read().split('Start Date: ') #Split the data file at Start Dates
            for dataset in range(1, len(datasets)):
                theData = datasets[dataset]
                thisDate = (datetime.strptime(theData[0:8], "%m/%d/%y")).strftime("%Y-%m-%d")
                thisDate = thisDate.replace('-','')
                if theData.find('\r\n'):
                    theData = theData.replace('\r\n', '\n')
                    splitOffData = theData.split('MSN:')
                    match = re.search('Subject: .*\n', splitOffData[0])
                    subject = match.group(0).split(':')[1].strip()
                    subject_list.append(subject)
                    variables = splitOffData[1].split('\n')
                    programname = variables.pop(0).strip()
                
                #if there is date needed to be remove from a ID's data
                #then skip all the extraction process below
                #only extract data that we need
                if rat_id == None:
                    pass
                else:
                    rat_id = [str(i) for i in rat_id] #force convert the value type inside the list
                    if str(subject) not in rat_id:
                        continue
                
                #recognize all defined variable name in MSN protocol
                MSN_folder = os.path.dirname(self.file)
                MSN = os.path.join(MSN_folder, programname+'.MPC')
                try:
#                    os.path.exists(MSN):
                    TS_var_name_map = {}
                    arrayA_name_map = {}
                    with open(MSN, 'r') as f:
                        for n, line in enumerate(f):
                            if 'DIM' in line:
                                pat = re.compile(r'(DIM\s+)(\w)([\s=\d]*)([\s\\]*)(\w*\s*\w*)(\s+)([\w\(\)]*)')
                                var, name = pat.search(line).group(2), pat.search(line).group(5)
                                if var != 'A':
                                    if name != '':
                                        name = re.sub('[\s]*', '', name)
                                        TS_var_name_map[var] = "(%s)"%var+name
                            elif re.match(r'\s+\\\sA\(\d*\)', line):
                                pat = re.compile(r'(\s+\\\s)(A\()(\d*)(\))\W*([\w\s\(\)]*)([\w\s\(\),\/]*)')
                                idx, name = pat.search(line).group(3), pat.search(line).group(5)
                                arrayA_name_map[idx]='A(%s)'%idx+name.strip('\n')
                                varnameLists =  [line for line in variables if not re.search('\w:\s+', line) and line != '']
                    #find common variable names between MSN protocol and datafile
                    common_vars = [var.strip(":") for var in varnameLists if var.strip(":") in TS_var_name_map.keys()]
                    #assume array A is alwasy store working variables
                    common_vars += ['A']
                    common_vars.sort()  #sort the common variables to make sure they are in order
                    data_dict = {}
    #                variables = [value for value in variables if not re.match(r'[A-Z]:\s+0.0+', value)] #delete all empty variables
                    for idx, var in enumerate(common_vars, 1):
                        if idx < len(common_vars):
                            start = variables.index(common_vars[idx-1]+":")
                            end = variables.index(common_vars[idx]+":")
                            data = variables[start+1:end]
                        else:
                            start = variables.index(common_vars[idx-1]+":")
                            data = variables[start+1:]
                        temp = []
    
                        for d in data:
                            if d!='':
                                temp += re.split('\s+',d.split(':')[1])
                                temp.remove('')
                            #convert str --> numbers
                        data_dict[var.strip(':')] =  pd.to_numeric(pd.Series(temp, name = var.strip(':')))
                    alldata_dict[subject] = data_dict
                except:
                    print ('Pleas provide MSN programe in the data folder: %s'%MSN)
                
        self.date = thisDate

        TS_df_dict = {}
        workingVar_dict = {}
        for rat, data_d in alldata_dict.items():
            temp_df_list = []
            for var, nm in TS_var_name_map.items():
                data_d[var].name = nm
                temp_df_list.append(data_d[var])     
            TS_df_dict[rat] = pd.concat(temp_df_list,axis = 1)
            
            temp2 = {}
            for k, nm in arrayA_name_map.items():
                try:
                    temp2[nm] = data_d['A'].iloc[int(k)]
                except IndexError:
                    print ('%s in MSN (%s) cannnot find in file %s'%(nm,programname,self.file))
                    temp2[nm] = np.nan
            workingVar_dict[rat] = temp2
           
        if self.save:
            file_path = os.path.dirname(self.file)
            filename = os.path.join(file_path, '%s.xlsx'%thisDate)
            if os.path.exists(filename): #if the file has exists
                #first exame whether it contains the subject above
                x1 = pd.ExcelFile(filename)
                overlap = list(set(x1.sheet_names) & set(TS_df_dict.keys()))
                #if yes, replace the existed subject data
                if len(overlap) > 0:
                    if self.replace:
                        with pd.ExcelWriter(filename, mode = 'r', engine='openpyxl') as writer:
                            for sheet in overlap:
                                TS_df_dict[sheet].to_excel(writer, sheet_name = sheet, index = False)
                        print ('Replace MED-PC data file to an existing local excel file %s'%filename)
                    else:
                        print ('No action for an existing local excel file %s'%filename)
                #else, append new subject into this excel
                new = list(set(TS_df_dict.keys())^set(overlap))
                if len(new) > 0:
                    with pd.ExcelWriter(filename, mode = 'a', engine='openpyxl') as writer:
                        for sheet in new:
                            TS_df_dict[sheet].to_excel(writer, sheet_name = sheet, index=False) 
                    print ('Append MED-PC data file to an existing local excel file %s'%filename)
            else:
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    for sheet, df in TS_df_dict.items():
                        df.to_excel(writer, sheet_name = sheet, index=False)
                    print ('Extract MED-PC data file to a new local excel file %s'%file_path)
        
        return TS_df_dict, workingVar_dict
        
    def __add_trial_index (self, df, trial_ref_df):
        """
        Input:
            1. df
            2. ref_df
        Example:
            new_df = add_trial_num (df, reference_dict)
        """
        #convert reference dataframe to renference ditc
        ref_df = trial_ref_df.copy() #prevent mutate the original dataframe
        ref_df.set_index('Trial type', inplace = True)
        ref_df = ref_df['Ref col']
        reference_dict = ref_df.to_dict()
        #reconstruct trial index and add into subject dataframe
        key = list(reference_dict.keys())
        all_ref = pd.concat([df[reference_dict[k]].dropna() for k in key], keys = key)
        all_ref.name = 'TS'
        all_ref.sort_values(inplace=True)
        all_ref_df = all_ref.to_frame()
        all_ref_df.reset_index (inplace = True)
        all_ref_df['trial#'] = all_ref_df.index + 1
        temp = df.copy()
        for trial, col in reference_dict.items():
            temp_trial = all_ref_df[all_ref_df['level_0']==trial]
            temp['trial#_%s'%trial] = temp[col][temp[col].notnull()].apply(lambda x: temp_trial['trial#'][temp_trial['TS']==x].values[0])
        return temp
    
    
    def get_subj_df (self, ID, trial_ref_df):
        subj_df = pd.DataFrame()
        try:
            subj_df = self.df_dict[ID]
        except:
            try:
                subj_df = self.df_dict[str(ID)]
            except:
                print ("%s doesn't contain rat %s"%(self.file, ID))
        if len(subj_df) != 0:
            if len(trial_ref_df) != 0:
                subj_df = self.__add_trial_index (subj_df, trial_ref_df)
        return subj_df
