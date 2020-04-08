"""
Audio Labeling Tool
-------------------------

AI Diagostics Ltd
@author: Kevin Machado

Created on Wed Apr  8 17:29:31 2020
"""
import sys
import numpy as np 
import pandas as pd
import pyqtgraph as pg
import sounddevice as sd
import scipy.io.wavfile as wf
# GUI libraries
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtWidgets, QtGui
# Own Lobrary
import aidiagnostics_toolbox as aidt

class mainWindow(QMainWindow):
    def __init__(self):
        #Inicia el objeto QMainWindow
        QMainWindow.__init__(self)
        # Loads an .ui file & configure UI
        loadUi("PCG_ui_2.ui",self)
        #
#        _translate = QtCore.QCoreApplication.translate
#        QMainWindow.setWindowTitle('AID')
        # Variables
        self.fs = None
        self.data = None
        self.data_P1 = None
        self.vlabel = None                 # Vector Label
        self.duration = None
        self.vectortime = None
        self.file_path = str
        self.plot_colors = ['#ffee3d' , '#0072bd', '#d95319', '#bd0000']
        # Initial sub-functions
        self._configure_plot()
        self.buttons()
        
    
    def _update_plot(self):
        """
        Updates and redraws the graphics in the plot.
        """
        self.duration = np.size(self.data) * (1/self.fs)
        self.vectortime = np.linspace(0, self.duration, np.size(self.data))

        self.data_P1 = aidt.vec_nor(self.data)
        self.vlabel = np.zeros(len(self.data_P1))
        
        Xf1 = 1+aidt.butter_bp_fil(self.data_P1, 40, 70, self.fs)
        Xf2 = 2+aidt.butter_bp_fil(self.data_P1, 70, 100, self.fs)
        # Updating Plots
        self._plt1.clear()
        self._plt1.plot(x=list(self.vectortime), y=list(self.data_P1), pen=self.plot_colors[0])
        #self._plt1.plot(x=list(self.vectortime), y=list(self.vlabel), pen=self.plot_colors[0])
        self._plt1.plot(x=list(self.vectortime), y=list(self.vlabel), pen=self.plot_colors[2])
        self._plt2.clear()
        self._plt2.plot(x=list(self.vectortime), y=list(self.data_P1), pen=self.plot_colors[0])
        self._plt2.plot(x=list(self.vectortime), y=list(Xf1), pen=self.plot_colors[1])
        self._plt2.plot(x=list(self.vectortime), y=list(Xf2), pen=self.plot_colors[2])
        
#        self._plt3.clear()
#        self._plt3.plot(x=list(self.vectortime), y=list(self.vlabel), pen=self.plot_colors[0])
        # Add the LinearRegionItem to the ViewBox, but tell the ViewBox to exclude this 
        # item when doing auto-range calculations.
        self._plt1.addItem(self.region, ignoreBounds=True)      
        self._plt2.setAutoVisible(y=True)
        
        self._plt2.addItem(self.region2, ignoreBounds=True) 
        
        self._plt2.addItem(self.vLine, ignoreBounds=True)
        self._plt2.addItem(self.hLine, ignoreBounds=True)
        
        self.vb = self._plt2.vb
        self.proxy = pg.SignalProxy(self._plt2.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
    # ------------------------------------------------------------------------
                                     # Buttons
    # ------------------------------------------------------------------------
    def buttons(self):
        """
        Configures the connections between signals and UI elements.
        """
        self.openButton.clicked.connect(self.openF)
        self.playButton.clicked.connect(self.playB)
        self.stopButton.clicked.connect(self.stopB)
        self.labelButton.clicked.connect(self.setLabelB)
        self.saveLabelButton.clicked.connect(self.saveLabelB)
        self.loadLabelButton.clicked.connect(self.loadLabelB) 
    def openF(self):
        """
        open a box to browse the audio file. Then converts the file into list 
        to properly read the path of the audio file 
        """
        self.file_path, _ = QtGui.QFileDialog.getOpenFileName(self, 'Open File')
        # NOTE: add an error box to saying "the audio format file most be WAV"
        self.fs, self.data = wf.read(self.file_path)
        sd.default.samplerate=self.fs
        print(self.fs)
        # plots the signal loaded
        self._update_plot()  
    def playB(self):
        """
        play the audio file 
        """
        print('playing PCG audio', self.fs)
        sd.play(self.data,self.fs)    
    def stopB(self):
        """
        play the audio file 
        """
        print('stoping PCG audio')
        sd.stop()   
    def setLabelB(self):
        """
        Set the label in the label vector
        """
        lv = self.label_value_sb.value()       
        idx1 = np.abs(self.vectortime-self.minX2).argmin()
        idx2 = np.abs(self.vectortime-self.maxX2).argmin()
        # uploading the label vector
        self.vlabel[idx1:idx2] = lv
        self._plt1.clear()
        self._plt1.plot(x=list(self.vectortime), y=list(self.data_P1), pen=self.plot_colors[0])
        self._plt1.addItem(self.region, ignoreBounds=True)
        self._plt1.plot(x=list(self.vectortime), y=list(self.vlabel), pen=self.plot_colors[2])
        """
            In the future, we as patients are going to be able to recollect the physiological information of our body at home,
            and be able to bring that information to our GP consultations so medical professional can take better a real medical history
            and by so take better desisions
        """
    def saveLabelB(self):
        """
        Save the label vector
        """
        labels_address, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save File")#,"CSV Files (*.csv)")
        labels_p = pd.DataFrame(self.vlabel)
        labels_p.to_csv(labels_address)
    def loadLabelB(self):
        """
        Load a saved label vector
        """
        labels_address, _ = QtGui.QFileDialog.getOpenFileName(self, "Open Label File") #,"CSV Files (*.csv)")
        labels_loaded = pd.read_csv(labels_address)
        self.vlabel = labels_loaded.values[:,1]
        # Plotting Loaded labels
        self._plt1.clear()
        self._plt1.plot(x=list(self.vectortime), y=list(self.data_P1), pen=self.plot_colors[0])
        self._plt1.addItem(self.region, ignoreBounds=True)
        self._plt1.plot(x=list(self.vectortime), y=list(self.vlabel), pen=self.plot_colors[2])
    # ------------------------------------------------------------------------
                            # Plot Configuration
    # ------------------------------------------------------------------------
    def _configure_plot(self):
        """
        Configures specific elements of the PyQtGraph plots.
        :return:
        """
        #self.mainW = pg.GraphicsWindow(title='Spectrogram', size=(800,600))
        
        #QMainWindow.setObjectName("AID")
#        self.label = pg.LabelItem(justify='right')
#        _mainWindow.addItem(self.label)
        self.plt1.setBackground(background=None)
        self.plt1.setAntialiasing(True)
        self._plt1 = self.plt1.addPlot(row=1, col=1)
        self._plt1.setLabel('bottom', "Tiempo", "s")
        self._plt1.setLabel('left', "Amplitud", "Volt")
        self._plt1.showGrid(x=False, y=False)
        
        self.plt2.setBackground(background=None)
        self.plt2.setAntialiasing(True)
        self._plt2 = self.plt2.addPlot(row=1, col=1)
        self._plt2.setLabel('bottom', "Tiempo", "s")
        self._plt2.setLabel('left', "Amplitud", "Volt")
        self._plt2.showGrid(x=False, y=False)
        
        # Region 1 
        self.region = pg.LinearRegionItem()
        self.region.setZValue(1)
        
        self.region.sigRegionChanged.connect(self.update)
        self._plt2.sigRangeChanged.connect(self.updateRegion)
        self.region.setRegion([0, 4])
        # Setting Region 2
        self.region2 = pg.LinearRegionItem()
        self.region2.setZValue(1)
        self.region2.setRegion([0, 0.5])
               
        self.region2.sigRegionChanged.connect(self.update2)
        
        # cross hair
        self.vLine = pg.InfiniteLine(angle=90, movable=False, pen=[100,100,200,200])
        self.hLine = pg.InfiniteLine(angle=0, movable=False, pen=[100,100,200,200])
    # ------------------------------------------------------------------------
                             # Process - Updates
    # ------------------------------------------------------------------------    
    def update(self):
        self.region.setZValue(1)
        minX, maxX = self.region.getRegion()     # get the min-max values of region
        self._plt2.setXRange(minX, maxX, padding=0)
    
    def updateRegion(self, window, viewRange):
        rgn = viewRange[0]
        self.region.setRegion(rgn)
    
    def update2(self):
        self.region2.setZValue(-10)
        self.minX2, self.maxX2 = self.region2.getRegion()     # get the min-max values of region
#        self.label.setText("<span style='font-size: 12pt'>L1=%0.1f,   <span style='color: red'>L2=%0.1f</span>,   <span style='color: green'>L1-L2=%0.1f</span>" % (self.minX2, self.maxX2, abs(self.minX2-self.maxX2)))
        #self._plt4.setXRange(minX3, maxX3, padding=0)
        
    def updateRegion2(self, window, viewRange):
        rgn_f = viewRange[0]
        self.region3.setRegion(rgn_f)
    
    def mouseMoved(self, evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if self._plt2.sceneBoundingRect().contains(pos):
            mousePoint = self.vb.mapSceneToView(pos)
            #index = int(mousePoint.x())
            #if index > 0 and index < len(self.data):
            #print(mousePoint.x())
                    #label.setText("<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>,   <span style='color: green'>y2=%0.1f</span>" % (mousePoint.x(), data1[index], data2[index]))
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())
        
#Instancia para iniciar una aplicacion en windows
app = QApplication(sys.argv)
#debemos crear un objeto para la clase creada arriba
_mainWindow = mainWindow()
    #muestra la ventana
_mainWindow.show()
    #ejecutar la aplicacion
app.exec_()