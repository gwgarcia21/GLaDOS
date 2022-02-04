from pyo import *
from pydub import AudioSegment
import numpy as np

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

def calc_pitch_shift(semitone, freq):
    shift = semitone - freq
    shift = np.float32(shift)
    shift = convert_numpy_to_standard(shift)
    return shift

def convert_numpy_to_standard(val):
    if isinstance(val, np.generic):
        return np.asscalar(val)

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
    return

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