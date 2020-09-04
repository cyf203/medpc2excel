# coding: utf-8


import sys
import re  #for word processing
import pandas as pd    #for data loading and manipulation
import os #for access folder
import numpy as np   #for calculaiton
import matplotlib as mpl
import matplotlib.pyplot as plt
import mplcursors
import dill
# from openpyxl import load_workbook
from datetime import datetime
from collections import defaultdict
Tree= lambda: defaultdict(Tree)
from PyQt5 import QtCore, QtGui, QtWidgets  #QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from medpc2excel.medpc_read import medpc_read

#%% Utilities Class
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
                    print ('getting file on %s'%(start))
        
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

#%% UI code
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 812)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMaximumSize(QtCore.QSize(800, 812))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabs = QtWidgets.QTabWidget(self.centralwidget)
        self.tabs.setGeometry(QtCore.QRect(10, 10, 781, 791))
        self.tabs.setDocumentMode(False)
        self.tabs.setTabsClosable(False)
        self.tabs.setMovable(True)
        self.tabs.setTabBarAutoHide(False)
        self.tabs.setObjectName("tabs")
        self.genExcel = QtWidgets.QWidget()
        self.genExcel.setObjectName("genExcel")
        self.widget = QtWidgets.QWidget(self.genExcel)
        self.widget.setGeometry(QtCore.QRect(9, 10, 761, 751))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.datafolder_button = QtWidgets.QPushButton(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.datafolder_button.sizePolicy().hasHeightForWidth())
        self.datafolder_button.setSizePolicy(sizePolicy)
        self.datafolder_button.setObjectName("datafolder_button")
        self.horizontalLayout_2.addWidget(self.datafolder_button)
        self.datafolder_path_input = QtWidgets.QTextEdit(self.widget)
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
        self.medpctoexcel_button = QtWidgets.QPushButton(self.widget)
        self.medpctoexcel_button.setObjectName("medpctoexcel_button")
        self.horizontalLayout.addWidget(self.medpctoexcel_button)
        self.override = QtWidgets.QComboBox(self.widget)
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
        self.medpctoexcel_progressbar = QtWidgets.QProgressBar(self.widget)
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
        self.log = QtWidgets.QTextBrowser(self.widget)
        self.log.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.log.setLineWrapColumnOrWidth(0)
        self.log.setObjectName("log")
        self.verticalLayout.addWidget(self.log)
        self.tabs.addTab(self.genExcel, "")
        self.dataexplorer = QtWidgets.QWidget()
        self.dataexplorer.setObjectName("dataexplorer")
        self.widget1 = QtWidgets.QWidget(self.dataexplorer)
        self.widget1.setGeometry(QtCore.QRect(9, 9, 761, 751))
        self.widget1.setObjectName("widget1")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.widget1)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.horizontalLayout_6.setSpacing(6)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.load_datafile = QtWidgets.QPushButton(self.widget1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.load_datafile.sizePolicy().hasHeightForWidth())
        self.load_datafile.setSizePolicy(sizePolicy)
        self.load_datafile.setObjectName("load_datafile")
        self.horizontalLayout_6.addWidget(self.load_datafile)
        self.datafile_path = QtWidgets.QTextEdit(self.widget1)
        self.datafile_path.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.datafile_path.sizePolicy().hasHeightForWidth())
        self.datafile_path.setSizePolicy(sizePolicy)
        self.datafile_path.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.datafile_path.setFont(font)
        self.datafile_path.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.datafile_path.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.datafile_path.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.datafile_path.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.datafile_path.setTabChangesFocus(True)
        self.datafile_path.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.datafile_path.setObjectName("datafile_path")
        self.horizontalLayout_6.addWidget(self.datafile_path)
        self.verticalLayout_3.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_input_ids = QtWidgets.QLabel(self.widget1)
        self.label_input_ids.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_input_ids.setObjectName("label_input_ids")
        self.horizontalLayout_7.addWidget(self.label_input_ids)
        self.input_ids = QtWidgets.QTextEdit(self.widget1)
        self.input_ids.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.input_ids.sizePolicy().hasHeightForWidth())
        self.input_ids.setSizePolicy(sizePolicy)
        self.input_ids.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.input_ids.setFont(font)
        self.input_ids.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.input_ids.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.input_ids.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.input_ids.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.input_ids.setTabChangesFocus(True)
        self.input_ids.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.input_ids.setObjectName("input_ids")
        self.horizontalLayout_7.addWidget(self.input_ids)
        self.verticalLayout_3.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.update_events_list_Button = QtWidgets.QPushButton(self.widget1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.update_events_list_Button.sizePolicy().hasHeightForWidth())
        self.update_events_list_Button.setSizePolicy(sizePolicy)
        self.update_events_list_Button.setMinimumSize(QtCore.QSize(0, 32))
        self.update_events_list_Button.setMaximumSize(QtCore.QSize(200, 16777215))
        self.update_events_list_Button.setObjectName("update_events_list_Button")
        self.horizontalLayout_8.addWidget(self.update_events_list_Button)
        self.events_combo = QtWidgets.QComboBox(self.widget1)
        self.events_combo.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.events_combo.sizePolicy().hasHeightForWidth())
        self.events_combo.setSizePolicy(sizePolicy)
        self.events_combo.setMinimumSize(QtCore.QSize(200, 30))
        self.events_combo.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.events_combo.setMaxVisibleItems(30)
        self.events_combo.setObjectName("events_combo")
        self.horizontalLayout_8.addWidget(self.events_combo)
        self.verticalLayout_3.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.label_select_events = QtWidgets.QLabel(self.widget1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_select_events.sizePolicy().hasHeightForWidth())
        self.label_select_events.setSizePolicy(sizePolicy)
        self.label_select_events.setMaximumSize(QtCore.QSize(100, 31))
        self.label_select_events.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_select_events.setObjectName("label_select_events")
        self.horizontalLayout_11.addWidget(self.label_select_events)
        self.add_events_Button = QtWidgets.QPushButton(self.widget1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.add_events_Button.sizePolicy().hasHeightForWidth())
        self.add_events_Button.setSizePolicy(sizePolicy)
        self.add_events_Button.setMinimumSize(QtCore.QSize(3, 32))
        self.add_events_Button.setMaximumSize(QtCore.QSize(25, 16777215))
        self.add_events_Button.setObjectName("add_events_Button")
        self.horizontalLayout_11.addWidget(self.add_events_Button)
        self.input_events = QtWidgets.QTextEdit(self.widget1)
        self.input_events.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.input_events.sizePolicy().hasHeightForWidth())
        self.input_events.setSizePolicy(sizePolicy)
        self.input_events.setMinimumSize(QtCore.QSize(80, 0))
        self.input_events.setMaximumSize(QtCore.QSize(1000, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.input_events.setFont(font)
        self.input_events.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.input_events.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.input_events.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.input_events.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.input_events.setTabChangesFocus(True)
        self.input_events.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.input_events.setObjectName("input_events")
        self.horizontalLayout_11.addWidget(self.input_events)
        self.verticalLayout_3.addLayout(self.horizontalLayout_11)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_sessiondur = QtWidgets.QLabel(self.widget1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_sessiondur.sizePolicy().hasHeightForWidth())
        self.label_sessiondur.setSizePolicy(sizePolicy)
        self.label_sessiondur.setMaximumSize(QtCore.QSize(150, 16777215))
        self.label_sessiondur.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_sessiondur.setObjectName("label_sessiondur")
        self.horizontalLayout_9.addWidget(self.label_sessiondur)
        self.input_session_dur = QtWidgets.QTextEdit(self.widget1)
        self.input_session_dur.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.input_session_dur.sizePolicy().hasHeightForWidth())
        self.input_session_dur.setSizePolicy(sizePolicy)
        self.input_session_dur.setMaximumSize(QtCore.QSize(100, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.input_session_dur.setFont(font)
        self.input_session_dur.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.input_session_dur.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.input_session_dur.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.input_session_dur.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.input_session_dur.setTabChangesFocus(True)
        self.input_session_dur.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.input_session_dur.setObjectName("input_session_dur")
        self.horizontalLayout_9.addWidget(self.input_session_dur)
        self.horizontalLayout_10.addLayout(self.horizontalLayout_9)
        spacerItem = QtWidgets.QSpacerItem(100, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem)
        self.plot = QtWidgets.QPushButton(self.widget1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plot.sizePolicy().hasHeightForWidth())
        self.plot.setSizePolicy(sizePolicy)
        self.plot.setMaximumSize(QtCore.QSize(16777215, 32))
        self.plot.setObjectName("plot")
        self.horizontalLayout_10.addWidget(self.plot)
        self.verticalLayout_3.addLayout(self.horizontalLayout_10)
        self.verticalLayout_4.addLayout(self.verticalLayout_3)
        self.graphicsView = QtWidgets.QGraphicsView(self.widget1)
        self.graphicsView.setObjectName("graphicsView")
        self.verticalLayout_4.addWidget(self.graphicsView)
        self.tabs.addTab(self.dataexplorer, "")
        self.genVar = QtWidgets.QWidget()
        self.genVar.setObjectName("genVar")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.genVar)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.load_configfile_button = QtWidgets.QPushButton(self.genVar)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.load_configfile_button.sizePolicy().hasHeightForWidth())
        self.load_configfile_button.setSizePolicy(sizePolicy)
        self.load_configfile_button.setObjectName("load_configfile_button")
        self.horizontalLayout_3.addWidget(self.load_configfile_button)
        self.configpath_input = QtWidgets.QTextEdit(self.genVar)
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
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.genTSfile_button = QtWidgets.QPushButton(self.genVar)
        self.genTSfile_button.setObjectName("genTSfile_button")
        self.horizontalLayout_4.addWidget(self.genTSfile_button)
        self.genTSfile_progressbar = QtWidgets.QProgressBar(self.genVar)
        self.genTSfile_progressbar.setProperty("value", 0)
        self.genTSfile_progressbar.setAlignment(QtCore.Qt.AlignCenter)
        self.genTSfile_progressbar.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.genTSfile_progressbar.setObjectName("genTSfile_progressbar")
        self.horizontalLayout_4.addWidget(self.genTSfile_progressbar)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.genVar_button = QtWidgets.QPushButton(self.genVar)
        self.genVar_button.setObjectName("genVar_button")
        self.horizontalLayout_5.addWidget(self.genVar_button)
        self.genVar_progressbar = QtWidgets.QProgressBar(self.genVar)
        self.genVar_progressbar.setProperty("value", 0)
        self.genVar_progressbar.setAlignment(QtCore.Qt.AlignCenter)
        self.genVar_progressbar.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.genVar_progressbar.setObjectName("genVar_progressbar")
        self.horizontalLayout_5.addWidget(self.genVar_progressbar)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        self.log_2 = QtWidgets.QTextBrowser(self.genVar)
        self.log_2.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.log_2.setLineWrapColumnOrWidth(0)
        self.log_2.setObjectName("log_2")
        self.verticalLayout_2.addWidget(self.log_2)
        self.tabs.addTab(self.genVar, "")
        self.tab_help = QtWidgets.QWidget()
        self.tab_help.setObjectName("tab_help")
        self.info_label = QtWidgets.QLabel(self.tab_help)
        self.info_label.setGeometry(QtCore.QRect(10, 10, 1071, 151))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setItalic(True)
        self.info_label.setFont(font)
        self.info_label.setTextFormat(QtCore.Qt.PlainText)
        self.info_label.setObjectName("info_label")
        self.tabs.addTab(self.tab_help, "")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.tabs.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.log, self.tabs)
        MainWindow.setTabOrder(self.tabs, self.datafolder_button)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Behavior Data Extracter"))
        self.datafolder_button.setText(_translate("MainWindow", "Data folder"))
        self.medpctoexcel_button.setText(_translate("MainWindow", "MED-PC to Excel"))
        self.override.setItemText(0, _translate("MainWindow", "Override"))
        self.override.setItemText(1, _translate("MainWindow", "Replace"))
        self.override.setItemText(2, _translate("MainWindow", "Append"))
        self.medpctoexcel_progressbar.setFormat(_translate("MainWindow", "%p%"))
        self.tabs.setTabText(self.tabs.indexOf(self.genExcel), _translate("MainWindow", "Generate Excel"))
        self.load_datafile.setText(_translate("MainWindow", "Load file"))
        self.label_input_ids.setText(_translate("MainWindow", "Input IDs (e.g, 64,65)"))
        self.update_events_list_Button.setText(_translate("MainWindow", "Update event list (based on the 1st ID)"))
        self.label_select_events.setText(_translate("MainWindow", "Add Selected Events"))
        self.add_events_Button.setText(_translate("MainWindow", ">>"))
        self.label_sessiondur.setText(_translate("MainWindow", "Session duration (mins)"))
        self.plot.setText(_translate("MainWindow", "Plot"))
        self.tabs.setTabText(self.tabs.indexOf(self.dataexplorer), _translate("MainWindow", "Data Explorer"))
        self.load_configfile_button.setText(_translate("MainWindow", "Load Config.xlsm file"))
        self.genTSfile_button.setText(_translate("MainWindow", "Generate TS file"))
        self.genTSfile_progressbar.setFormat(_translate("MainWindow", "%p%"))
        self.genVar_button.setText(_translate("MainWindow", "Generate Variables"))
        self.genVar_progressbar.setFormat(_translate("MainWindow", "%p%"))
        self.tabs.setTabText(self.tabs.indexOf(self.genVar), _translate("MainWindow", "Generate Variable"))
        self.info_label.setText(_translate("MainWindow", "Current version v2.0.2 \n"
"Created by Yifeng Cheng, Ph.D. \n"
"Contact:\n"
"(979)571-8531\n"
"cyfhopkins@gmail.com\n"
"ycheng62@jhu.edu"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_help), _translate("MainWindow", "Help"))
#%% Functional Code
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
        self.load_datafile.clicked.connect(self.__load_exceldata_file_frombutton)
        self.update_events_list_Button.clicked.connect(self.__update_events_list_frombutton)
        self.add_events_Button.clicked.connect(self.__add_select_events_frombutton)
        self.plot.clicked.connect(self.__dataexplorer)
        self.currentTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    #stream output to text PYQT5 text widgets
    def on_myStream_message(self, message):
        self.log.append (message)
    
    ################################################
    # Tab 1 functions
    ################################################
    def __set_data_folder_frombutton(self):
        path_frombutton = QtWidgets.QFileDialog.getExistingDirectory()
        self.datafolder_path_input.clear()
        self.datafolder_path_input.append(path_frombutton)
        #options = QtWidgets.QFileDialog.Options()
        #options = QtWidgets.QFileDialog.DontUseNativeDialog
        self.datafolder = path_frombutton
        self.log.append (self.currentTime+'>>\t'+'Set data folder: %s'%self.datafolder)
    
    def __run_medpc2excel(self):
        datafolder = self.datafolder_path_input.toPlainText()

        #get path for all *. data file
        files = explore(datafolder,*[''],kernalmsg=False)
        #get a list of data file
        datafile_list = files.get_dir_list(display=False)
        self.log.append (self.currentTime+'>>\t'+'Found %s files'%(len(datafile_list)))
        override = str(self.override.currentText()) 
        if override == 'Override':
            replace_file = True
            replace_data  = True
        elif override == 'Replace':
            replace_file = False
            replace_data = True
        elif override == 'Append':
            replace_file = False
            replace_data = False
        
        total = len(datafile_list)
        func_out = ''
        for n, f in enumerate(datafile_list):
            #get all data from this session
            _, func_out = medpc_read(f, override = replace_file, replace = replace_data, log = func_out) #pass TS_df_tree to an anonymous variable
            self.medpctoexcel_progressbar.setValue(n/total*100)
        self.medpctoexcel_progressbar.setValue(100)
        self.log.append(func_out)
    
    ################################################
    # Tab 2 functions
    ################################################
    def __load_exceldata_file_frombutton(self):
        options = QtWidgets.QFileDialog.Options()
        self.filepath, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Load data file", "","*.xlsx;;All Files (*)", options=options)
        self.datafile_path.clear()
        self.datafile_path.append(self.filepath)
        
        return None
    
    def __update_events_list_frombutton (self):
        rat_ids_str = self.input_ids.toPlainText()
        file = self.filepath
        self.data_explr_rat_ids = rat_ids_str.split(',')
        rat_ids = self.data_explr_rat_ids
        # read data
        try:
            self.data_explr_df_dict = {rat: pd.read_excel(file, sheet_name = str(rat)) for rat in rat_ids}
        except:
            QMessageBox.about(self, 'Error', 'Invalid IDs or filepath')
        colname = list(self.data_explr_df_dict[rat_ids[0]].columns)
        
        self.events_combo.clear()
        self.events_combo.addItems(colname)
        self.events_combo.update()

        return None
    
    def __add_select_events_frombutton (self):
        select_event = self.events_combo.currentText()
        current_event = self.input_events.toPlainText()
        if current_event == '':
            new_event = select_event
        else:
            new_event = current_event + ',' + select_event
        self.input_events.clear()
        self.input_events.insertPlainText(new_event)
        # self.input_events.append(select_event+',')
        
        return None
    
    def __dataexplorer (self):
        # rat_ids_str = self.input_ids.toPlainText()
        # rat_ids = rat_ids_str.split(',')
        events_str = self.input_events.toPlainText()
        sessiondur_str = self.input_session_dur.toPlainText()
        target_event = events_str.split(',')
        session_time_min = float(sessiondur_str)
        
        # file = self.filepath

        # df_dict = {rat: pd.read_excel(file, sheet_name = str(rat)) for rat in rat_ids}
        rat_ids = self.data_explr_rat_ids
        df_dict = self.data_explr_df_dict
        
        #Load plot configuration
        mpl.rcParams['font.family'] = 'Arial Narrow'
        mpl.rcParams['axes.linewidth'] = 1
        mpl.rcParams['axes.spines.left'] = True
        mpl.rcParams['axes.spines.right'] = False
        mpl.rcParams['axes.spines.top'] = False
        # mpl.rcParams['axes.titlepad'] = 10
        # mpl.rcParams['xtick.labelsize']= 10 
        # mpl.rcParams['ytick.labelsize'] =10
        # mpl.rcParams['xtick.major.pad'] = 3
        # mpl.rcParams['ytick.major.pad'] = 3
        # mpl.rcParams['axes.labelpad'] = 2
        # mpl.rcParams['pdf.fonttype'] = 42 #!!!this is important for generate a clear text figure for illustrator editing
        
        color_list = ['#9BC2E6',
                      '#FFD966',
                      '#EE6112',
                      '#A9D08E',
                      '#DD6FC5',
                      '#66FFCC',
                      '#FF33CC',
                      '#0099FF',
                      '#FFC000',
                      '#993366']   # Support up to 10 events
        
        fig, axes = plt.subplots(len(rat_ids),1, sharex = True, sharey = False)
        
        # fig1.set_size_inches(8.5, 7)
        
        for fig_n, rat in enumerate(rat_ids):
            if len(rat_ids) == 1:
                ax = axes
            else:
                ax = axes[fig_n]
            
            df = df_dict[rat]
            
            label_pos = []
            labels = []
            for n,e in enumerate(target_event):
                x = df[e].values
                ax.eventplot(x/60, orientation = 'horizontal', lineoffsets = (n+0.5), linelengths = 0.8, linewidths = 0.5, color = color_list[n])
                label_pos.append(n+0.5)
                labels.append(e[3:])
                
            #spine visibility
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            if fig_n != (len(rat_ids)-1):
                ax.spines['bottom'].set_visible(False)
                ax.tick_params (bottom = False)
            else:   
                ax.spines['bottom'].set_visible(True)
                ax.set_xlabel('Time (mins)')
                
            ax.set_title('Rat %s'%(rat))
            
            ax.tick_params(left = False)
            ax.set_ylim(0,n+1)
            ax.set_yticks(label_pos)
            ax.set_yticklabels(labels)
            ax.set_xlim(-0.5, session_time_min+0.5)
                
        mplcursors.cursor(highlight=True).connect("add", lambda sel: sel.annotation.set_text(sel.artist.get_label()))
        # fig1.patch.set_facecolor('none')
        # fig1.patch.set_alpha(0)
        fig.tight_layout()
        plt.close()
       
        scene = QtWidgets.QGraphicsScene()
        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas, self)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(canvas)
        layout.addWidget(toolbar)
        
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        scene.addWidget(widget)
        self.graphicsView.setScene(scene)
        
    
    
    ################################################
    # Tab 3 functions
    ################################################
    
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
        self.log_2.append (self.currentTime+'>>\t'+'%s locates in %s'%(filename+'.pkl',filedir))

    def __load_configfile_frombutton(self):
        options = QtWidgets.QFileDialog.Options()
        #options = QtWidgets.QFileDialog.DontUseNativeDialog
        self.configfile, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Load config.xlsm file", "","config (*.xlsm);;All Files (*)", options=options)
        self.configpath_input.clear()
        self.configpath_input.append(self.configfile)
        self.log_2.append (self.currentTime+'>>\t'+'Loaded config.xlsm file: %s'%(self.configfile))
        
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
        self.log_2.append (self.currentTime+'>>\t'+'Found %s files'%(len(datafile_list)))
        
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
            self.log_2.append (self.currentTime+'>>\t'+'Reading data from %s'%os.path.basename(f))
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
                        
                        self.log_2.append ('\t'+'\t'+'Rat %s data extracted'%ID)
                    else:
                        self.log_2.append ('\t'+'\t'+'Find duplicate date for rat %s: %s'%(ID, date))
            else:
                self.log_2.append ('\t'+'\t'+'No wanted data')
            
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
                self.log_2.append (self.currentTime+'>>\t'+'Dump data to local excel file. Location: %s'%fname)

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
            self.log_2.append (self.currentTime+'>>\t'+'No timestample file')

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
