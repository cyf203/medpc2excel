import re  #for word processing
import pandas as pd    #for data loading and manipulation
import os #for access folder
import numpy as np   #for calculaiton
from openpyxl import load_workbook
from datetime import datetime
from collections import defaultdict
Tree= lambda: defaultdict(Tree)

def medpc_read (file, rat_id=None, save=True, replace = True, log=''):
    '''
    Inputs:
    1. file (str, path)
    2. rat_id   (array like)
    3. save (Bolean value,default is True)
    4. replace  (Bolean value, default is True)

    Outputs:
    1. TS_df_tree (a tree, like {'date':{'rat':df}})
    2. log (string, capture essential events)

    Example:
    TS_df_tree, log =  medpc2excel (r'C:\20200229_test', replace = False)

    '''
    alldata_tree = Tree()
    subject_list= []
    MSN_dict={}
    nowtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    #load raw file into dict
    with open(file, 'r') as f:
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
                match2 = re.search('Box: .*\n', splitOffData[0])
                box = match2.group(0).split(':')[1].strip()
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
            MSN_folder = os.path.dirname(file)
            MSN = os.path.join(MSN_folder, programname+'.MPC')
            try:
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
            
            except:
                log += nowtime+'>>\t'+'Error!Pleas provide MSN programe in the data folder: %s'%MSN +'\n'
            
            varnameLists =  [line for line in variables if not re.search('\w:\s+', line) and line != '']
            #find common variable names between MSN protocol and datafile
            common_vars = [var.strip(":") for var in varnameLists if var.strip(":") in TS_var_name_map.keys()]
            #assume array A is alwasy store working variables
            common_vars += ['A']
            common_vars.sort()  #sort the common variables to make sure they are in order
            data_dict = {}
            
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
                data_dict[var.strip(':')] =  pd.to_numeric(pd.Series(temp, name = var.strip(':'),dtype = float))
            alldata_tree[thisDate][subject] = data_dict
            
            if thisDate not in MSN_dict.keys():
                MSN_dict[thisDate] = pd.DataFrame({'ID':[subject],'Box':[box],'MSN':[programname]})
            else:
                MSN_dict[thisDate] = MSN_dict[thisDate].append({'ID':subject,'Box':box,'MSN':programname},ignore_index=True)

    TS_df_tree = Tree()
    workingVar_tree = Tree() #computed, but not return for this version
    for d, alldata_dict in alldata_tree.items():
        for rat, data_d in alldata_dict.items():
            temp_df_list = []
            for var, nm in TS_var_name_map.items():
                data_d[var].name = nm
                temp_df_list.append(data_d[var])     
            TS_df_tree[d][rat] = pd.concat(temp_df_list,axis = 1)
            
            temp2 = {}
            for k, nm in arrayA_name_map.items():
                try:
                    temp2[nm] = data_d['A'].iloc[int(k)]
                except IndexError:
                    log += nowtime+'>>\t'+'Error!%s in MSN (%s) cannnot find in file %s'%(nm,programname,file) + '\n'
                    temp2[nm] = np.nan
            workingVar_tree[d][rat] = temp2
        
    if save:
        file_path = os.path.dirname(file)
        for d, TS_df_dict in TS_df_tree.items():
            filename = os.path.join(file_path, '%s.xlsx'%d)
            if os.path.exists(filename): #if the file has exists
                #first exame whether it contains the subject above
                x1 = pd.ExcelFile(filename)
                overlap = list(set(x1.sheet_names) & set(TS_df_dict.keys()))
                #if yes, replace the existed subject data
                if len(overlap) > 0:
                    if replace:
                        with pd.ExcelWriter(filename, mode = 'r', engine='openpyxl') as writer: # pylint: disable=abstract-class-instantiated
                            MSN_dict[d].to_excel(writer,sheet_name='MSNs',index=False)
                            for sheet in overlap:
                                TS_df_dict[sheet].to_excel(writer, sheet_name = sheet, index = False)
                            log += nowtime+'>>\t'+'Replace MED-PC data file to an existing local excel file %s'%filename +'\n'
                    else:
                        log += nowtime+'>>\t'+'No action for an existing local excel file %s'%filename+'\n'
                
                else:
                    #else, append new subject into this excel
                    new = list(set(TS_df_dict.keys())^set(overlap))
                    if len(new) > 0:
                        MSNs_file = pd.read_excel(filename,sheet_name = 'MSNs')
                        if MSNs_file.values.shape == MSN_dict[d].values.shape:
                            if np.prod(np.equal(MSNs_file.astype(str).values,MSN_dict[d].astype(str).values)):
                                MSN_same = True
                            else:
                                MSN_same = False
                        else:    
                            MSN_same = False
                        if ~MSN_same: #if two MSNs summary are not the same append current one to the file one
                            book = load_workbook(filename)
                            writer = pd.ExcelWriter(filename, engine = 'openpyxl')
                            writer.book = book
                            writer.sheets = {ws.title: ws for ws in book.worksheets if ws.title=='MSNs'} #get MSNs sheet from existing excel
                            MSN_dict[d].to_excel(writer, sheet_name = 'MSNs', startrow = writer.sheets['MSNs'].max_row, header = None, index= False)
                            writer.save()
                            writer.close()
                        with pd.ExcelWriter(filename, mode = 'a', engine='openpyxl') as writer: # pylint: disable=abstract-class-instantiated
                            for sheet in new:
                                TS_df_dict[sheet].to_excel(writer, sheet_name = sheet, index=False) 
                            log += nowtime+'>>\t'+'Append MED-PC data file to an existing local excel file %s'%filename +'\n'
            else:
                with pd.ExcelWriter(filename, engine='openpyxl') as writer: # pylint: disable=abstract-class-instantiated
                    MSN_dict[d].to_excel(writer,sheet_name='MSNs',index=False)
                    for sheet, df in TS_df_dict.items():
                        df.to_excel(writer, sheet_name = sheet, index=False)
                    log += nowtime+'>>\t'+'Extract MED-PC data file to a new local excel file %s'%file_path+'\n'
    
    return TS_df_tree, log
