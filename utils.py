fundamentals=[16.35,17.32,18.35,19.45,20.60,21.83,23.12,24.50,25.96,27.50,29.14,30.87,32.70,34.65,36.71,38.89,41.20,43.65,46.25,49.00,51.91,55.00,58.27,61.74,65.41,69.30,73.42,77.78,82.41,87.31,92.50,98.00,103.83,110.00,116.54,123.47,130.81,138.59,146.83,155.56,164.81,174.61,185.00,196.00,207.65,220.00,233.08,246.94,261.63,277.18,293.66,311.13,329.63,349.23,369.99,392.00,415.30,440.00,466.16,493.88,523.25,554.37,587.33,622.25,659.25,698.46,739.99,783.99,830.61,880.00,932.33,987.77,1046.50,1108.73,1174.66,1244.51,1318.51,1396.91,1479.98,1567.98,1661.22,1760.00,1864.66,1975.53,2093.00,2217.46,2349.32,2489.02,2637.02,2793.83,2959.96,3135.96,3322.44,3520.00,3729.31,3951.07,4186.01,4434.92,4698.63,4978.03,5274.04,5587.65,5919.91,6271.93,6644.88,7040.00,7458.62,7902.13]

import chunk
import numpy as np
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    #return array[idx]
    return array[idx]

#def calc_pitch_shift(freq):
#    semitone = find_nearest(fundamentals, freq)
#    shift = semitone - freq
#    shift = np.float32(shift)
#    #print(type(shift))
#    shift = convert_numpy_to_standard(shift)
#    return shift

def calc_pitch_shift(semitone, freq):
    #semitone = 164.81
    shift = semitone - freq
    shift = np.float32(shift)
    #print(type(shift))
    shift = convert_numpy_to_standard(shift)
    return shift

def convert_numpy_to_standard(val):
    if isinstance(val, np.generic):
        return np.asscalar(val)

import math
def octave_difference(src_freq, dst_freq):
    if dst_freq == 0:
        return 0
    ratio = dst_freq / src_freq
    octave = math.log(ratio) / math.log(2)
    return octave

import re
def tryint(s):
    try:
        return int(s)
    except:
        return s

def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]

def sort_nicely(l):
    """ Sort the given list in the way that humans expect.
    """
    l.sort(key=alphanum_key)
    return np.array(l)

import wave

def pitch_modulation():
    wr = wave.open('download.wav', 'r')
    # Set the parameters for the output file.
    par = list(wr.getparams())
    print(par)
    #par[3] = 0  # The number of samples will be set by writeframes.
    par = tuple(par)
    ww = wave.open('wave_proc.wav', 'w')
    ww.setparams(par)

    fr = 10
    sz = wr.getframerate()//fr  # Read and process 1/fr second at a time.
    # A larger number for fr means less reverb.
    c = int(wr.getnframes()/sz)  # count of the whole file
    shift = 100//fr  # shifting 100 Hz
    for num in range(c):
        da = np.fromstring(wr.readframes(sz), dtype=np.int16)
        left, right = da[0::2], da[1::2]  # left and right channel
        lf, rf = np.fft.rfft(left), np.fft.rfft(right)
        lf, rf = np.roll(lf, shift), np.roll(rf, shift)
        lf[0:shift], rf[0:shift] = 0, 0
        nl, nr = np.fft.irfft(lf), np.fft.irfft(rf)
        ns = np.column_stack((nl, nr)).ravel().astype(np.int16)
        ww.writeframes(ns.tostring())

    wr.close()
    ww.close()
    return

from pydub import AudioSegment

def pitch_modulation_pydub():
    sound = AudioSegment.from_file('chunks\chunk10.wav', format="wav")

    # shift the pitch up by half an octave (speed will increase proportionally)
    octaves = 0.08

    new_sample_rate = int(sound.frame_rate * (2.0 ** octaves))

    # keep the same samples but tell the computer they ought to be played at the 
    # new, higher sample rate. This file sounds like a chipmunk but has a weird sample rate.
    hipitch_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})

    # now we just convert it to a common sample rate (44.1k - standard audio CD) to 
    # make sure it works in regular audio players. Other than potentially losing audio quality (if
    # you set it too low - 44.1k is plenty) this should now noticeable change how the audio sounds.
    hipitch_sound = hipitch_sound.set_frame_rate(44100)

    #export / save pitch changed sound
    hipitch_sound.export("chunks\pydub_proc.wav", format="wav")

def pitch_modulation_chunk(chunks_path:str, proc_chunk_path:str, shift:float):
    print(chunks_path)
    print(shift)
    sound = AudioSegment.from_file(chunks_path, format="wav")

    # shift the pitch up by half an octave (speed will increase proportionally)
    #octaves = shift / 12.0
    octaves = shift
    #if shift != 0.0:
        #octaves = shift / 10.0

    new_sample_rate = int(sound.frame_rate * (2.0 ** octaves))

    # keep the same samples but tell the computer they ought to be played at the 
    # new, higher sample rate. This file sounds like a chipmunk but has a weird sample rate.
    hipitch_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})

    # now we just convert it to a common sample rate (44.1k - standard audio CD) to 
    # make sure it works in regular audio players. Other than potentially losing audio quality (if
    # you set it too low - 44.1k is plenty) this should now noticeable change how the audio sounds.
    hipitch_sound = hipitch_sound.set_frame_rate(44100)

    #export / save pitch changed sound
    hipitch_sound.export(proc_chunk_path, format="wav")