"""
AI Diagostics Ltd
@author: Kevin Machado

Created on Wed Apr  8 17:29:31 2020
Module file containing Python definitions and statements
"""

# Libraries
import numpy as np
from scipy.signal import lfilter, butter


# -----------------------------------------------------------------------------
# PDS
# -----------------------------------------------------------------------------
def vec_nor(x):
    """
    Normalize the amplitude of a vector from -1 to 1
    """
    nVec = np.zeros(len(x));		   # Initializate derivate vector
    nVec = np.divide(x, max(x))
    nVec = nVec-np.mean(nVec);
    nVec = np.divide(nVec,np.max(nVec));
        
    return nVec

# -----------------------------------------------------------------------------
# Filter Processes
# -----------------------------------------------------------------------------
def butter_bp_coe(lowcut, highcut, fs, order=1):
    """
    Butterworth passband filter coefficients b and a
    Ref: 
    [1] https://timsainb.github.io/spectrograms-mfccs-and-inversion-in-python.html
    [2] https://gist.github.com/kastnerkyle/179d6e9a88202ab0a2fe
    """
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_bp_fil(data, lowcut, highcut, fs, order=1):
    """
    Butterworth passband filter
    Ref: 
    [1] https://timsainb.github.io/spectrograms-mfccs-and-inversion-in-python.html
    [2] https://gist.github.com/kastnerkyle/179d6e9a88202ab0a2fe
    """
    b, a = butter_bp_coe(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return vec_nor(y)
