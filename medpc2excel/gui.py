# coding: utf-8


import sys
import re  #for word processing
import pandas as pd    #for data loading and manipulation
import os #for access folder
import numpy as np   #for calculaiton
import dill
from openpyxl import load_workbook
from datetime import datetime
from collections import defaultdict
Tree= lambda: defaultdict(Tree)
from PyQt5 import QtCore, QtGui, QtWidgets  #QtCore, QtGui

from medpc2excel.medpc_read import medpc_read

#%% Maincode
class explore:
    def __init__ (self, target_dir, *extension, kernalmsg = True):
        self.rootdir = target_dir
        self.ext = tuple(extension)
        self.p = kernalmsg
        self.get_dir_list(display=False)
        
    def get_dir_list (self, date_range = (), display = True):
        #ext = tuple (extension)
        if len(date_range) > 0:
            if len(date_range) == 2:
                start, end = date_range
                if self.p:
                    print ('getting files between %s to %s'%(start, end))
            elif len(date_range) == 1:
                start = date_range[0]
                end = start
                if self.p:
                    print ('getting file on %s'%(start, end))
        
        else:
            if self.p:
                print ('Scanning all files')
            start = 0
            end = np.inf
        
        allFile_l = []    
        for subdir, dirs, files in os.walk(self.rootdir):
            for file in files:
                #exclude configuration file no matter how
                if 'config' not in file:
                    #if file has extension
                    if self.ext != ('',) and self.ext != ():
                        pat = ".*\.%s"%self.ext
                        if re.match(pat,file):
                            if file.split('.')[0] >= str(start) and file.split('.')[0] <= str(end):
                                allFile_l.append(os.path.join(subdir,file))
                    #if file has no extension
                    elif not re.match(".*\..*", file):
                        if file.split('_')[0] >= str(start) and file.split('_')[0] <= str(end):
                            allFile_l.append(os.path.join(subdir,file))
        
        if display:
            if self.p:
                print ('Found %s %s files'%(len(allFile_l),self.ext))

        self.allFile_l = allFile_l
        return allFile_l
        
    def head(self, n = 5):
        #num_files = len(self.allFile_l)
        count= 0
        for num, f in enumerate (self.allFile_l, 1):
            if self.p:
                print (num,":",re.split('\\\\',f)[-2]+'\\'+re.split('\\\\',f)[-1])
            count += 1
            if count == n:
                break
        return 

#build a class to capture all the output 
class MyStream(QtCore.QObject):
    message = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        super(MyStream, self).__init__(parent)

    def write(self, message):
        self.message.emit(str(message))

#UI code
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(591, 812)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMaximumSize(QtCore.QSize(591, 812))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tab_GenVar = QtWidgets.QTabWidget(self.centralwidget)
        self.tab_GenVar.setGeometry(QtCore.QRect(10, 0, 571, 781))
        self.tab_GenVar.setDocumentMode(False)
        self.tab_GenVar.setTabsClosable(False)
        self.tab_GenVar.setMovable(True)
        self.tab_GenVar.setTabBarAutoHide(False)
        self.tab_GenVar.setObjectName("tab_GenVar")
        self.SessionAnalysis = QtWidgets.QWidget()
        self.SessionAnalysis.setObjectName("SessionAnalysis")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.SessionAnalysis)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.datafolder_button = QtWidgets.QPushButton(self.SessionAnalysis)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.datafolder_button.sizePolicy().hasHeightForWidth())
        self.datafolder_button.setSizePolicy(sizePolicy)
        self.datafolder_button.setObjectName("datafolder_button")
        self.horizontalLayout_2.addWidget(self.datafolder_button)
        self.datafolder_path_input = QtWidgets.QTextEdit(self.SessionAnalysis)
        self.datafolder_path_input.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.datafolder_path_input.sizePolicy().hasHeightForWidth())
        self.datafolder_path_input.setSizePolicy(sizePolicy)
        self.datafolder_path_input.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.datafolder_path_input.setFont(font)
        self.datafolder_path_input.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.datafolder_path_input.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.datafolder_path_input.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.datafolder_path_input.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.datafolder_path_input.setTabChangesFocus(True)
        self.datafolder_path_input.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.datafolder_path_input.setObjectName("datafolder_path_input")
        self.horizontalLayout_2.addWidget(self.datafolder_path_input)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.medpctoexcel_button = QtWidgets.QPushButton(self.SessionAnalysis)
        self.medpctoexcel_button.setObjectName("medpctoexcel_button")
        self.horizontalLayout.addWidget(self.medpctoexcel_button)
        self.override = QtWidgets.QComboBox(self.SessionAnalysis)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.override.sizePolicy().hasHeightForWidth())
        self.override.setSizePolicy(sizePolicy)
        self.override.setMinimumSize(QtCore.QSize(0, 23))
        self.override.setMaximumSize(QtCore.QSize(135, 31))
        self.override.setObjectName("override")
        self.override.addItem("")
        self.override.addItem("")
        self.override.addItem("")
        self.override.setItemText(2, "")
        self.horizontalLayout.addWidget(self.override)
        self.medpctoexcel_progressbar = QtWidgets.QProgressBar(self.SessionAnalysis)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.medpctoexcel_progressbar.sizePolicy().hasHeightForWidth())
        self.medpctoexcel_progressbar.setSizePolicy(sizePolicy)
        self.medpctoexcel_progressbar.setMinimumSize(QtCore.QSize(100, 0))
        self.medpctoexcel_progressbar.setProperty("value", 0)
        self.medpctoexcel_progressbar.setAlignment(QtCore.Qt.AlignCenter)
        self.medpctoexcel_progressbar.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.medpctoexcel_progressbar.setObjectName("medpctoexcel_progressbar")
        self.horizontalLayout.addWidget(self.medpctoexcel_progressbar)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.load_configfile_button = QtWidgets.QPushButton(self.SessionAnalysis)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.load_configfile_button.sizePolicy().hasHeightForWidth())
        self.load_configfile_button.setSizePolicy(sizePolicy)
        self.load_configfile_button.setObjectName("load_configfile_button")
        self.horizontalLayout_3.addWidget(self.load_configfile_button)
        self.configpath_input = QtWidgets.QTextEdit(self.SessionAnalysis)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.configpath_input.sizePolicy().hasHeightForWidth())
        self.configpath_input.setSizePolicy(sizePolicy)
        self.configpath_input.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.configpath_input.setFont(font)
        self.configpath_input.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.configpath_input.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.configpath_input.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.configpath_input.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.configpath_input.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.configpath_input.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.configpath_input.setTabChangesFocus(True)
        self.configpath_input.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.configpath_input.setObjectName("configpath_input")
        self.horizontalLayout_3.addWidget(self.configpath_input)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.genTSfile_button = QtWidgets.QPushButton(self.SessionAnalysis)
        self.genTSfile_button.setObjectName("genTSfile_button")
        self.horizontalLayout_4.addWidget(self.genTSfile_button)
        self.genTSfile_progressbar = QtWidgets.QProgressBar(self.SessionAnalysis)
        self.genTSfile_progressbar.setProperty("value", 0)
        self.genTSfile_progressbar.setAlignment(QtCore.Qt.AlignCenter)
        self.genTSfile_progressbar.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.genTSfile_progressbar.setObjectName("genTSfile_progressbar")
        self.horizontalLayout_4.addWidget(self.genTSfile_progressbar)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.genVar_button = QtWidgets.QPushButton(self.SessionAnalysis)
        self.genVar_button.setObjectName("genVar_button")
        self.horizontalLayout_5.addWidget(self.genVar_button)
        self.genVar_progressbar = QtWidgets.QProgressBar(self.SessionAnalysis)
        self.genVar_progressbar.setProperty("value", 0)
        self.genVar_progressbar.setAlignment(QtCore.Qt.AlignCenter)
        self.genVar_progressbar.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.genVar_progressbar.setObjectName("genVar_progressbar")
        self.horizontalLayout_5.addWidget(self.genVar_progressbar)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.log = QtWidgets.QTextBrowser(self.SessionAnalysis)
        self.log.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.log.setLineWrapColumnOrWidth(0)
        self.log.setObjectName("log")
        self.verticalLayout.addWidget(self.log)
        self.tab_GenVar.addTab(self.SessionAnalysis, "")
        self.tab_help = QtWidgets.QWidget()
        self.tab_help.setObjectName("tab_help")
        self.label_18 = QtWidgets.QLabel(self.tab_help)
        self.label_18.setGeometry(QtCore.QRect(10, 10, 1071, 151))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setItalic(True)
        self.label_18.setFont(font)
        self.label_18.setTextFormat(QtCore.Qt.PlainText)
        self.label_18.setObjectName("label_18")
        self.tab_GenVar.addTab(self.tab_help, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tab_GenVar.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.load_configfile_button, self.log)
        MainWindow.setTabOrder(self.log, self.tab_GenVar)
        MainWindow.setTabOrder(self.tab_GenVar, self.datafolder_button)
        MainWindow.setTabOrder(self.datafolder_button, self.genTSfile_button)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Behavior Data Extracter"))
        self.datafolder_button.setText(_translate("MainWindow", "Data folder"))
        self.medpctoexcel_button.setText(_translate("MainWindow", "MED-PC to Excel"))
        self.override.setItemText(0, _translate("MainWindow", "Override existing data"))
        self.override.setItemText(1, _translate("MainWindow", "Skip existing data"))
        self.medpctoexcel_progressbar.setFormat(_translate("MainWindow", "%p%"))
        self.load_configfile_button.setText(_translate("MainWindow", "Load Config.xlsm file"))
        self.genTSfile_button.setText(_translate("MainWindow", "Generate TS file"))
        self.genTSfile_progressbar.setFormat(_translate("MainWindow", "%p%"))
        self.genVar_button.setText(_translate("MainWindow", "Generate Variables"))
        self.genVar_progressbar.setFormat(_translate("MainWindow", "%p%"))
        self.tab_GenVar.setTabText(self.tab_GenVar.indexOf(self.SessionAnalysis), _translate("MainWindow", "Generate Variables"))
        self.label_18.setText(_translate("MainWindow", "Current version v1.0 \n"
"Created by Yifeng Cheng, Ph.D. \n"
"Contact:\n"
"(979)571-8531\n"
"cyfhopkins@gmail.com\n"
"ycheng62@jhu.edu"))
        self.tab_GenVar.setTabText(self.tab_GenVar.indexOf(self.tab_help), _translate("MainWindow", "Help"))


class MyApp (QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.datafolder_button.clicked.connect (self.__set_data_folder_frombutton)
        self.load_configfile_button.clicked.connect (self.__load_configfile_frombutton)
        self.medpctoexcel_button.clicked.connect(self.__run_medpc2excel)
        self.genTSfile_button.clicked.connect (self.__genTSfile)
        self.genVar_button.clicked.connect(self.__genvars)
        self.currentTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    #stream output to text PYQT5 text widgets
    def on_myStream_message(self, message):
        self.log.append (message)
    
    def __set_data_folder_frombutton(self):
        path_frombutton = QtWidgets.QFileDialog.getExistingDirectory()
        self.datafolder_path_input.clear()
        self.datafolder_path_input.append(path_frombutton)
        #options = QtWidgets.QFileDialog.Options()
        #options = QtWidgets.QFileDialog.DontUseNativeDialog
        self.datafolder = path_frombutton
        self.log.append (self.currentTime+'>>\t'+'Set data folder: %s'%self.datafolder)

    def __load_configfile_frombutton(self):
        options = QtWidgets.QFileDialog.Options()
        #options = QtWidgets.QFileDialog.DontUseNativeDialog
        self.configfile, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Load config.xlsm file", "","config (*.xlsm);;All Files (*)", options=options)
        self.configpath_input.clear()
        self.configpath_input.append(self.configfile)
        self.log.append (self.currentTime+'>>\t'+'Loaded config.xlsm file: %s'%(self.configfile))
    
    def __run_medpc2excel(self):
        datafolder = self.datafolder_path_input.toPlainText()

        #get path for all *. data file
        files = explore(datafolder,*[''],kernalmsg=False)
        #get a list of data file
        datafile_list = files.get_dir_list(display=False)
        self.log.append (self.currentTime+'>>\t'+'Found %s files'%(len(datafile_list)))
        override = str(self.override.currentText()) 
        if override == 'Override existing data':
            replace = True
        else:
            replace = False
        
        total = len(datafile_list)
        func_out = ''
        for n, f in enumerate(datafile_list):
            #get all data from this session
            _, func_out = medpc_read(f, replace = replace, log = func_out) #pass TS_df_tree to an anonymous variable
            self.medpctoexcel_progressbar.setValue(n/total*100)
        self.medpctoexcel_progressbar.setValue(100)
        self.log.append(func_out)

    def load_variable (self, mainfolder, filename):
        fname = os.path.join(mainfolder,'variables',filename+'.pkl')
        print (fname)
        with open(fname,'rb') as f:
            var = dill.load(f)
        return var    
    
    def dump_variable (self, mainfolder, filename, var):
        fname = os.path.join(mainfolder,'variables',filename+'.pkl')
        filedir = os.path.dirname(fname)
        if not os.path.exists(filedir):
            os.mkdir(filedir)
        with open(fname,'wb') as f:
            dill.dump(var,f)
        self.log.append (self.currentTime+'>>\t'+'%s locates in %s'%(filename+'.pkl',filedir))

   
    def __genTSfile(self):
        #>> Define datafolder and config file path
        datafolder = self.datafolder_path_input.toPlainText()
        config_excel = self.configpath_input.toPlainText()
        analysisfolder = os.path.dirname(config_excel) 
        
        #>> Data file explorer
        extension = 'xlsx'
        #get path for all data file
        files = explore(datafolder,*[extension],kernalmsg=False) 
        #get a list of data file
        datafile_list = files.get_dir_list(display=False)
        self.log.append (self.currentTime+'>>\t'+'Found %s files'%(len(datafile_list)))
        
        #>> DATA EXTRACTION
        #get rat id and filter
        ID_sheet = pd.read_excel(config_excel, sheet_name = 'ID').astype('str')
        ID_sheet.set_index('Rat id',inplace = True)
        rat_id = set(ID_sheet.index.tolist())

        #get block config
        block_sheet = pd.read_excel(config_excel, sheet_name = 'Block info')
        block = set(block_sheet['Block index'].tolist())
        try:
            block_info = block_sheet['Block info'].tolist()
        except:
            block_info = []

        #get trial info for recontrusct trial index
        try:
            trial_ref = pd.read_excel(config_excel, sheet_name = 'Trial info')
        except:
            trial_ref = pd.DataFrame()
        #get event config
        event_config_df = pd.read_excel(config_excel, sheet_name = 'Events')
        event_config_df = event_config_df[~event_config_df['Event name'].isna()]

        #>> define essential functions
        def index_session(table, value):
            if type(table) == pd.core.frame.DataFrame:
                temp = table[table.isin([value])].dropna(axis = 1, how = 'all').dropna(how = 'all')
                index = temp.stack().index.tolist()
            elif type(table) == pd.core.series.Series:
                index = table[table == value].index.tolist()
            return index

        def get_single_eventTS (df, event_col, trial_type, **kwargs):
            
            options = {
                        'criteria': '',
                        'block': '',
                        'bins': '',
                        'extend': 'nan',
                        }
            options.update(kwargs)
            #process the creiter
            pat = re.compile(r'(\S+\w+)\s*([!<>=]{1,2})\s*(\w+)')
            get_criteria = lambda c: (pat.search(c).group(1), pat.search(c).group(2), pat.search(c).group(3))
            criteria = options ['criteria']
            if criteria == '' or str(criteria) == 'nan':
                criterion_list = []
            else:
                criterion_list = [c for c in criteria.split(', ') if c != '' or c != None ]
            
            #get other paramter
            block = options['block']
            bins = options['bins']
            extend = options['extend']
                
            if str(extend) != 'nan':
                if block == '':
                    last = 9999
                    event_df = df[event_col].iloc[1:].append(pd.Series([last]),ignore_index=True)
                    mask = [True]*len(event_df)
                    if len(criterion_list) > 0:
                        for c in criterion_list:
                            c_col, operator, match = get_criteria(c)
                            mask = mask & eval('df[c_col]'+operator+match).reset_index()[c_col]
                else:
                    last = 9999
                    if bins*block >= len(df[event_col].dropna()):
                        last = 9999
                    else:
                        last = df[event_col].iloc[bins*block+1]
                    
                    event_df = df[event_col].iloc[1:].append(pd.Series([last]),ignore_index=True).iloc[int(bins*(block-1)):int(bins*block)]
                    
                    mask = [True]*len(event_df)
                    if len(criterion_list) > 0:
                        for c in criterion_list:
                            c_col, operator, match = get_criteria(c)
                            mask = mask & eval('df[c_col]'+operator+match).reset_index()[c_col].iloc[int(bins*(block-1)):int(bins*block)]
            else:
                if block == '':

                    event_df = df[event_col]
                        
                    mask = [True]*len(event_df)
                    if len(criterion_list) > 0:
                        for c in criterion_list:
                            c_col, operator, match = get_criteria(c)
                            mask = mask&eval('df[c_col]'+operator+match)
                else:

                    event_df = df[event_col].iloc[int(bins*(block-1)):int(bins*block)]
                        
                    mask = [True]*len(event_df)
                    if len(criterion_list) > 0:
                        for c in criterion_list:
                            c_col, operator, match = get_criteria(c)
                            mask = mask&eval('df[c_col]'+operator+match).iloc[int(bins*(block-1)):int(bins*block)]
            
            res_df = event_df[mask].dropna().copy()

            res_df.name = 'Event'
            return res_df

        def get_TS_df (df, config_df, block_list=[]):
            """
            Input:
                config_df  (col1: Event name, col2: Col name, col3: Criteria, col4: Extend)
            Return:
                df 
            """        
            if block_list==[]:
                rows = [r for _,r in config_df.iterrows()]
                res_list = [get_single_eventTS(df, r['Col name'], r['Trial type'],  criteria=r['Criteria'], extend = r['Extend']) for r in rows]
                key_list = [(str(r['Trial type']),r['Event name']) for r in rows]

                column_name = ['Trial', 'Event', 'Old idx', 'TS']
            else:
                rows = [r for _,r in config_df.iterrows()]
                res_list = [get_single_eventTS(df, r['Col name'], r['Trial type'], criteria=r['Criteria'], extend = r['Extend'], block = b, bins=r['Bin']) for r in rows for b in block_list]
                key_list = [(str(r['Trial type']),b, r['Event name']) for r in rows for b in block_list]

                column_name = ['Trial', 'Block', 'Event', 'Old idx', 'TS']
            
            concat_TS = pd.concat (res_list, keys = key_list)
            if type(concat_TS) == pd.Series:
                res_df = concat_TS.to_frame()
            else:
                res_df = concat_TS
            res_df.reset_index (inplace = True)
            res_df.columns = column_name
            del res_df['Old idx']
            return res_df
        
        #>> Extract data from local excel file
        catch = Tree() #catch all rat dataframe
        Event_TS_list = [] #store all event TS
        key_list = []

        total=len(datafile_list)

        for n, f in enumerate(datafile_list):
            date = os.path.basename(f).strip('.'+extension) #get the date for current file 
            self.log.append (self.currentTime+'>>\t'+'Reading data from %s'%os.path.basename(f))
            for ID in rat_id: #iterate rat id of what I want (from config excel)
                if str(date) in ID_sheet.loc[str(ID)].values: #Check if this file belongs to the rat
                    rat_df = pd.read_excel(f, sheet_name = str(ID))
                    idx_list = index_session(ID_sheet.loc[ID], date)
                    if len(idx_list) == 0:
                        continue
                    elif len(idx_list) == 1:
                        sidx = idx_list[0]
                        catch [sidx][ID] = rat_df
                        if len(block) == 0:
                            Event_TS_list.append(get_TS_df(rat_df, event_config_df))
                        else:
                            Event_TS_list.append(get_TS_df(rat_df, event_config_df,block_list = block))
                        
                        key_list.append((sidx,ID))
                        
                        self.log.append ('\t'+'\t'+'Rat %s data extracted'%ID)
                    else:
                        self.log.append ('\t'+'\t'+'Find duplicate date for rat %s: %s'%(ID, date))
            else:
                self.log.append ('\t'+'\t'+'No wanted data')
            
            self.genTSfile_progressbar.setValue(n/total*100)
        
        #>>Concatenate all data
        #Construct a dataframe for all events timestampe
        Event_TS_df = pd.concat(Event_TS_list, keys = key_list)
        Event_TS_df.reset_index(inplace=True)
        Event_TS_df.rename(columns = {'level_0':'Session','level_1':'ID'}, inplace = True)
        del Event_TS_df['level_2']

        #Add group column
        Event_TS_df.insert(1, 'Group', Event_TS_df['ID'].apply(lambda x: ID_sheet['Group'][ID_sheet.index == x].values[0]))

        def df2excel (mainfolder, subfolder, filename, df, sheetname, timetag = True):
            '''
            save one df into one excel
            '''
            if timetag:
                now = datetime.today().strftime('%Y%m%d_%H')
            else:
                now = ''
            fname = os.path.join(mainfolder, subfolder, filename+'_%s.xlsx'%now)
            filedir = os.path.dirname(fname)
            if not os.path.exists(filedir):
                os.mkdir(filedir)

            with pd.ExcelWriter(os.path.join(fname), engine='xlsxwriter') as writer: # pylint: disable=abstract-class-instantiated
                df.to_excel(writer, sheet_name = 'Events', index=False)
                self.log.append (self.currentTime+'>>\t'+'Dump data to local excel file. Location: %s'%fname)

        #Write dataframe into analysis folder
        self.dump_variable(analysisfolder, 'Event_TS_df', Event_TS_df)
        df2excel(analysisfolder,'','Timestampe file', Event_TS_df, 'Events')
        
        self.genTSfile_progressbar.setValue(100)
        
        return None
    
    def __genvars(self):
        
        def convert_formula (formula, addition):
            """
            Inputs:
                1. formula          (str)
                2. addition         (str, contains "%s")
            Return:
                1. mean_df          (pd.Dataframe)
            """
            op = re.compile(r'([-+*/!<>=()]{1,2})')
        #    split_formula = re.split(r'(\w+)', formula)
            split_formula = re.split(r'([+\-*\/^%() \t]+)', formula)
            for index, s in enumerate(split_formula):
                if s != '':
                    if op.findall(s):
                        pass
                    elif s.isdigit():
                        split_formula[index]=s
                    else:
                        split_formula[index]=addition%s
            new_formula = ''
            for s in split_formula:
                new_formula +=s
            return new_formula


        #>> LOAD DATA FILES
        datafolder = self.datafolder_path_input.toPlainText()
        config_excel = self.configpath_input.toPlainText()
        analysisfolder = os.path.dirname(config_excel)
        file_path = analysisfolder

        #>> SESSION BY SESSION ANALYSIS    
        #load concatenated Event_TS_df
        try:
            Event_TS_df=self.load_variable(file_path, 'Event_TS_df')
        except:
            self.log.append (self.currentTime+'>>\t'+'No timestample file')

        #get block config
        block_sheet = pd.read_excel(config_excel, sheet_name = 'Block info')
        block = set(block_sheet['Block index'].tolist())
        try:
            block_info = block_sheet['Block info'].tolist()
        except:
            block_info = []
        #prepare a raw data structure
        analysis_config_df = pd.read_excel(config_excel, sheet_name = 'Analysis')
        analysis_config_df = analysis_config_df[~analysis_config_df['Measurements'].isna()]
        #get session list
        session_list = set(Event_TS_df.Session.unique())
        ID_sheet = pd.read_excel(config_excel, sheet_name = 'ID').astype('str')
        ID_sheet.set_index('Rat id',inplace = True)
        rat_id = set(ID_sheet.index.tolist())
        raw = Tree()
        total = len(analysis_config_df)*len(rat_id)*len(session_list)
        outercount = 0
        middlecount = 0
        innercount = 0
        if len(block) == 0:
            for index, r in analysis_config_df.iterrows():
                raw[str(r['Trial type'])][r['Measurements']] = pd.DataFrame()
                for ID in rat_id:
                    for n in session_list:
                        try:
                            mask = ((Event_TS_df['ID'] == ID) 
                                    & (Event_TS_df['Session'] == n) 
                                    & (Event_TS_df['Trial'].astype('str') == str(r['Trial type'])))
                            temp = Event_TS_df[mask].copy()
                            if len(temp) > 0:
                                if r['Method'] == 'sum' or r['Method'] == 'proportion':
                                    formula = convert_formula(r['Calculation'], "temp['TS'][temp['Event'] == '%s'].count()")
                                    res = eval(formula)
                                elif r['Method'] == 'latency':
                                    formula = convert_formula(r['Calculation'], "temp['TS'][temp['Event'] == '%s'].values")
                                    res = eval(formula)
                                    res = res.mean()
                                elif r['Method'] == 'duration':
                                    formula = convert_formula(r['Calculation'], "temp['TS'][temp['Event'] == '%s'].values")
                                    res = eval(formula)
                                    res = res.sum()
                                raw[str(r['Trial type'])][r['Measurements']].at[n,ID] = res
                        except KeyError:
                            print ("Check the name in the <%s> is matched with Measurements: %s"%(formula,r['Measurements']))
                        innercount +=1
                    middlecount += 1
                outercount +=1
                self.genVar_progressbar.setValue((innercount+middlecount+outercount)/total*100)
       
        else:
            for index, r in analysis_config_df.iterrows():
                for b in block:
                    raw[str(r['Trial type'])][r['Measurements']][b] = pd.DataFrame()
                    for ID in rat_id:
                        for n in session_list:
                            try:
                                mask = ((Event_TS_df['ID'] == ID) 
                                        & (Event_TS_df['Session'] == n) 
                                        & (Event_TS_df['Trial'].astype('str') == str(r['Trial type']))
                                        & (Event_TS_df['Block'] == b))
                                temp = Event_TS_df[mask].copy()
                                if len(temp) > 0:
                                    if r['Method'] == 'sum' or r['Method'] == 'proportion':
                                        formula = convert_formula(r['Calculation'], "temp['TS'][temp['Event'] == '%s'].count()")
                                        res = eval(formula)
                                    elif r['Method'] == 'latency':
                                        formula = convert_formula(r['Calculation'], "temp['TS'][temp['Event'] == '%s'].values")
                                        res = eval(formula)
                                        res = res.mean()
                                    elif r['Method'] == 'duration':
                                        formula = convert_formula(r['Calculation'], "temp['TS'][temp['Event'] == '%s'].values")
                                        res = eval(formula)
                                        res = res.sum()
                                    raw[str(r['Trial type'])][r['Measurements']][b].at[n,ID] = res
                            except KeyError:
                                print ("Check the name in the <%s> is matched with Measurements: %s"%(formula,r['Measurements']))
                            innercount +=1
                        middlecount += 1
                    outercount +=1
                    self.genVar_progressbar.setValue((innercount+middlecount+outercount)/total*100)

        #>> Dump file into local disk
        self.dump_variable(analysisfolder, 'raw', raw)
        self.genVar_progressbar.setValue(100)
        

def run():
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()

    #remove '#' if you want to connect all terminal output to UI
    # myStream = MyStream()
    # myStream.message.connect(window.on_myStream_message)
    #sys.stdout = myStream 
       
    sys.exit(app.exec_())
    
    
if __name__ == "__main__":
    run()
