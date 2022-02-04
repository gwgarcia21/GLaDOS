from distutils.command.config import config
from numpy import empty
from pyo import *
import requests
from pydub import AudioSegment
from pydub.utils import make_chunks
import crepe
from scipy.io import wavfile

import matplotlib.pyplot as plt

import utils

def pitch_shift_up(path_wav):
    # Eleva a frequência do áudio completo
    proc_path_wav = "proc.wav"
    s = Server(audio="offline").boot()
    filedur = sndinfo(path_wav)[1]
    s.recordOptions(dur=filedur, filename=proc_path_wav)
    ifile = SfPlayer(path_wav)
    FreqShift(ifile, shift=15, mul=1.0).out()
    s.start()
    return proc_path_wav