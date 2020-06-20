import numpy as np
from PyQt5 import QtWidgets, QtMultimedia
from PyQt5.QtWidgets import QInputDialog, QFileDialog
from scipy.io import wavfile
import os
from task2 import Ui_MainWindow
from pop import Ui_otherwindow
import pyqtgraph as pg
import numpy as np
from scipy.fftpack import rfft, rfftfreq, irfft
from random import randint
from pyqtgraph import PlotWidget, plot, QtCore
import simpleaudio as sa
from PyQt5.QtCore import pyqtSlot
from cmath import rect
import sys
import sounddevice as sd
from numba import jit

class ApplicationWindow(QtWidgets.QMainWindow):
    original_sig = np.array([])
    original_complex= np.array([])
    modified_sig = np.array([])
    modified_complex = np.array([])
    freq = np.array([])
    output_sig1 = np.array([])
    output_sig2 = np.array([])
    sample_rate = 0
    rectangular = False
    hamming = False
    hanning = False
    loaded = False
    output1 = False
    output2 = False
    play1 = False
    play2 = False
    gains =np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
    levels = [1000,3000,5000,7000,9000,11000,13000,15000,17000,19000]




    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.ui = Ui_MainWindow()
        # self.ui2 = Graphs()
        self.ui.setupUi(self)
        # self.ui2.setupUi(self)
        self.ui.showsignal.clicked.connect(self.newwindow)
        self.ui.addfilesmb.triggered.connect(self.read_file)
        # self.dataline1 = self.ui.original_sign.pl

        self.boxarray = [ self.ui.Svalue1, self.ui.Svalue2, self.ui.Svalue3, self.ui.Svalue4,
                         self.ui.Svalue5,
                         self.ui.Svalue6, self.ui.Svalue7, self.ui.Svalue8, self.ui.Svalue9, self.ui.Svalue10]
        self.sliderarr = [ self.ui.Band1, self.ui.Band2, self.ui.Band3, self.ui.Band4, self.ui.Band5,
                          self.ui.Band6, self.ui.Band7, self.ui.Band8, self.ui.Band9, self.ui.Band10]

        self.Play = [self.ui.Play1, self.ui.Play2]
        self.Output = [self.ui.Output1, self.ui.Output2]

        for i in range (0,10):
            self.connect_sliders(i)
            if i < 2:
                self.connect_play(i)
                self.connect_output(i)
        # combobox for changing between modes of opreation
        self.ui.comboBox.currentIndexChanged.connect(self.combobox)
        self.ui.actionzeroall.triggered.connect(self.zeroall)
        self.ui.pbzeroall.clicked.connect(self.zeroall)
        self.ui.load.clicked.connect(self.read_file)
        self.ui.actionLoad.triggered.connect(self.read_file)
        self.ui.actionAdd_Files.triggered.connect(self.read_file)
        self.ui.actionClear.triggered.connect(self.clear)
        # the graph in main window
        self.data_line = self.ui.modified_frequ.plot()
        # play and stop buttons
        self.ui.Playbutton.clicked.connect(self.play_audio)
        self.ui.Stopbutton.clicked.connect(self.stop_audio)
        # save button
        self.ui.savept.clicked.connect(self.save_file)





    def connect_sliders(self,i):
        self.sliderarr[i].valueChanged.connect(lambda: self.slidervalue(i))

    def connect_play(self,i):
        self.Play[i].toggled.connect(lambda: self.switch_audio(i+1))

    def connect_output(self,i):
        self.Output[i].toggled.connect(lambda: self.switch_output(i+1))
        print(1)

    def newwindow(self):
        self.window = QtWidgets.QMainWindow()
        self.ui2 = Ui_otherwindow()
        self.ui2.setupUi(self.window)
        if self.loaded :
            self.ui2.original_sign.plot(self.original_sig)
            self.ui2.original_frequ.plot(abs(self.original_complex))
            if not (self.output_sig1.size == 0):
                self.ui2.output1_sig.plot(irfft(self.output_sig1), pen= pg.mkPen(color=(170,0,0)))
                self.ui2.output11.plot(abs(self.output_sig1), pen= pg.mkPen(color=(170,0,0)))
            if not (self.output_sig2.size == 0):
                self.ui2.output2_sig.plot(irfft(self.output_sig2), pen= pg.mkPen(color=(0,250,0)))
                self.ui2.output22.plot(abs(self.output_sig2), pen= pg.mkPen(color=(0,250,0)))
            if (not (self.output_sig2.size == 0)) and (not (self.output_sig1.size == 0)):
                self.ui2.diff_sig.plot(np.subtract(irfft(self.output_sig1), irfft(self.output_sig2)),
                                       pen=pg.mkPen(color=(0, 25, 159)))
                self.ui2.diff_freq.plot(np.subtract(abs(self.output_sig1), abs(self.output_sig2)),
                                        pen=pg.mkPen(color=(0, 25, 159)))
        else:
            pass
        self.window.show()

    def read_file(self):
        filename = QFileDialog.getOpenFileName(self, "Open Song", "~", "Sound Files ( *.wav )")
        if filename[0] == "":
            pass
        else:
            self.sample_rate, self.original_sig = wavfile.read(filename[0])
            if self.original_sig.ndim == 2:
                self.original_sig = np.mean(self.original_sig, axis=1)
            else:
                pass
            self.loaded = True
            self.convert_freq()

    def convert_freq(self):
        self.original_complex = rfft(self.original_sig)
        self.modified_complex= np.copy(self.original_complex)
        self.freq = (rfftfreq(len(self.original_complex) + 1, 1 / self.sample_rate))
        self.freq = self.freq[self.freq > 0]
        print(self.freq[len(self.freq)-1])
        self.data_line.setData(self.freq,abs(self.modified_complex))
        self.ui.modified_frequ.setXRange(0,20000)




    def slidervalue(self, x):
        value = self.sliderarr[x].value()
        self.boxarray[x].setText(str(value))
        self.modify_signal(x, value)

    def switch_output(self,b):
        if b == 1:
            if self.ui.Output1.isChecked() == True:
                print(2)
                self.output1 = True
                self.output2 = False
        if b == 2:
            if self.ui.Output2.isChecked() == True:
                self.output2 = True
                self.output1 = False

    def switch_audio(self,b):
        if b == 1:
            if self.ui.Play1.isChecked() == True:
                self.play1 = True
                self.play2 = False
        if b == 2:
            if self.ui.Play2.isChecked() == True:
                self.play2 = True
                self.play1 = False






    def update_plot(self):
        self.data_line.setData(self.freq,abs(self.modified_complex))




    def save_file(self):
        if self.output1:
            self.output_sig1 = np.copy(self.modified_complex)
            wavfile.write("output1.wav", self.sample_rate,self.output_sig1)
        elif self.output2:
            self.output_sig2 = np.copy(self.modified_complex)
            wavfile.write("output2.wav", self.sample_rate, self.output_sig2)
        else:
            pass



    def combobox(self):
        option = self.ui.comboBox.currentIndex()
        if option == 0:
            self.zeroall()
        elif option == 1:
            self.rectangular = True
            self.hamming = False
            self.hanning = False
            self.zeroall()
            self.data_line.setData(self.freq, abs(self.original_complex))
        elif option == 2:
            self.rectangular = False
            self.hamming = True
            self.hanning = False
            self.zeroall()
        elif option == 3:
            self.rectangular = False
            self.hamming = False
            self.hanning = True
            self.zeroall()

    def zeroall(self):
        for x in range(0, 10):
            self.sliderarr[x].setValue(0)
        self.modified_complex = np.copy(self.original_complex)
        for i in range(0, 10):
            self.gains[i] = 1.0

    def draw():
        self.data_line.setData()



    def play_audio(self):
        if self.loaded:
            if self.play1:
                sd.play(irfft(self.output_sig1)/ irfft(self.output_sig1).max() , self.sample_rate)
            elif self.play2:
                sd.play(irfft(self.output_sig2) / irfft(self.output_sig2).max(), self.sample_rate)
            else:
                sd.play(irfft(self.modified_complex)/ irfft(self.modified_complex).max(), self.sample_rate)

    def stop_audio(self):
        sd.stop()

    def clear(self):
        print("x")
        self.data_line.setData([], [])
        self.output_sig1, self.output_sig2, self.original_complex, self.modified_complex, self.freq, self.original_sig = np.array(
            []), np.array([]), np.array([]), np.array([]), np.array([]), np.array([])
        self.loaded = False

    def hamm_signal(self, endp, startp,level,  gain):
        start = np.where(self.freq > startp)[0][0]
        end = np.where(self.freq > endp)[0][0]
        lenth = (end - start)
        actual_start = start-lenth//2
        actual_end = end+ lenth//2
        p1 = np.subtract(self.modified_complex[actual_start:start], (self.original_complex[actual_start: start]*np.hamming(lenth*2)[0:lenth//2] * self.gains[level]))
        p2 = np.subtract(self.modified_complex[end:actual_end], (self.original_complex[end: actual_end]*np.hamming(lenth*2)[6*lenth//4:2*lenth] * self.gains[level]))
        self.gains[level] =  gain
        self.modified_complex[actual_start:actual_end] = np.copy(self.original_complex[actual_start:actual_end])
        temp = np.copy(self.modified_complex)
        if gain == 1:
            pass
        else:
            temp[actual_start:actual_end] = temp[actual_start:actual_end] * np.hamming(lenth*2) * gain
            temp[actual_start:start] = np.add (temp[actual_start:start],p1)
            temp[end:actual_end] = np.add (temp[end:actual_end],p2)
        self.modified_complex[actual_start:actual_end] = np.copy(temp[actual_start:actual_end])
        self.update_plot()


    def hann_signal(self, endp, startp, level,gain):
        start = np.where(self.freq > startp)[0][0]
        end = np.where(self.freq > endp)[0][0]
        lenth = (end - start)
        actual_start = start - lenth // 2
        actual_end = end + lenth // 2
        p1 = np.subtract(self.modified_complex[actual_start:start], (self.original_complex[actual_start: start] * np.hanning(lenth * 2)[0:lenth // 2] * self.gains[level]))
        p2 = np.subtract(self.modified_complex[end:actual_end], (self.original_complex[end: actual_end] * np.hanning(lenth * 2)[6 * lenth // 4:2 * lenth] *self.gains[level]))
        self.gains[level] = gain
        self.modified_complex[actual_start:actual_end] = np.copy(self.original_complex[actual_start:actual_end])
        temp = np.copy(self.modified_complex)
        if gain == 1:
            pass
        else:
            temp[actual_start:actual_end] = temp[actual_start:actual_end] * np.hanning(lenth * 2) * gain
            temp[actual_start:start] = np.add(temp[actual_start:start], p1)
            temp[end:actual_end] = np.add(temp[end:actual_end], p2)
        self.modified_complex[actual_start:actual_end] = np.copy(temp[actual_start:actual_end])
        self.update_plot()


    def rectan_signal(self, endp, startp, level, gain):
        start = np.where(self.freq > startp)[0][0]
        end = np.where(self.freq > endp)[0][0]
        self.modified_complex [start:end] = self.modified_complex[start:end] / self.gains[level]
        self.gains[level] = gain
        self.modified_complex[start:end] = self.modified_complex[start:end] * self.gains[level]
        self.update_plot()


    def modify_signal(self, level, decibl):
        if self.loaded:
            gain = pow(10, (decibl / 20))
            if self.rectangular:
                for i in range(0,10):
                    if level == i:
                        self.rectan_signal(self.levels[i] + 1000, self.levels[i] - 1000, level, gain)
            elif self.hamming:
                for i in range (0,10):
                    if level == i:
                        self.hamm_signal(self.levels[i]+1000, self.levels[i]-1000, level, gain)
            elif self.hanning:
                for i in range (0,10):
                    if level == i:
                        self.hann_signal(self.levels[i] + 1000, self.levels[i] - 1000, level, gain)
        else:
            pass


def main():
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()

    app.exec_()


if __name__ == "__main__":
    main()
