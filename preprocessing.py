import numpy as np
from scipy import signal

class Preprocessor: #VERİYİ ALACAK, FİLTRELEYECEK VE TEMİZLEYECEK SINIF
    def __init__(self,data,fs=250): #başlatıcı
        self.data=data
        self.fs=fs
    # Bandpass Filter(1-40 Hz)
    def bandpass_filter(self,lowcut=1,hightcut=40,order=4):
        nyquist=0.5*self.fs
        low=lowcut/nyquist
        hight=hightcut/nyquist

        b,a = signal.butter(order, [low, hight],btype='band')
        filtered =signal.filtfilt(b, a, self.data)
        return filtered
    
    #notch filter (50 Hz)
    def notch_filter(self, freq=50, quality=30):
        b, a = signal.iirnotch(freq, quality, self.fs)
        filtered = signal.filtfilt(b, a, self.data)
        return filtered
    
    # 3. Normalization
    def normalize(self, data):
        normalized = (data - np.mean(data)) / np.std(data)
        return normalized.astype("float32")

    # FULL PIPELINE
    def preprocess(self):
        filtered = self.bandpass_filter()
        filtered = self.notch_filter()
        normalized = self.normalize(filtered)

        return normalized.astype("float32")