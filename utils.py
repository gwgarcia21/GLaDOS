import numpy as np
import math
import re
from pydub import AudioSegment
import os

def find_nearest(array, value):
    """ Encontra o valor mais próximo do desejado no array
    """
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

def octave_difference(src_freq, dst_freq):
    """ Calcula a diferença em oitavas (ou frações de oitava) de uma frequência para outra
    """
    if dst_freq == 0:
        return 0
    ratio = dst_freq / src_freq
    octave = math.log(ratio) / math.log(2)
    return octave

def sort_nicely(l):
    """ Organiza a lista como esperam os humanos
    """
    def tryint(s):
        try:
            return int(s)
        except:
            return s
    def alphanum_key(s):
        """ Transforma uma string em uma lista de strings e número de chunks
            "z23a" -> ["z", 23, "a"]
        """
        return [ tryint(c) for c in re.split('([0-9]+)', s) ]
    l.sort(key=alphanum_key)
    return np.array(l)

def pitch_modulation_chunk(chunks_path:str, proc_chunk_path:str, shift:float):
    """ Modula o pitch de uma parte do áudio para eliminar entonações
    """
    #print(chunks_path)
    #print(shift)
    sound = AudioSegment.from_file(chunks_path, format="wav")

    # shift the pitch up by half an octave (speed will increase proportionally)
    octaves = shift

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

    os.remove(chunks_path)
    
    return