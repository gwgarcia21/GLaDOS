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

def request_tts(text):
    # Requisição GET com texto desejado
    data = {
        'msg': text,
        'lang': 'Kimberly', 
        'source': 'ttsmp3' 
    }
    response = requests.post('https://ttsmp3.com/makemp3_new.php', data=data)
    #print(response.json())
    res = response.json()
    mp3_link = ""
    if 'MP3' in res:
        mp3_link = res['MP3']
    return mp3_link

def download_mp3(mp3_link, path):
    query = {
        'mp3': mp3_link,
        'location': 'direct'
    }
    response = requests.get('https://ttsmp3.com/dlmp3.php', params=query)
    with open(path, 'wb') as file:
        file.write(response.content)
    return

def convert_mp3_to_wav(path_mp3, path_wav):
    # Convert mp3 to wav                                                             
    sound = AudioSegment.from_mp3(path_mp3)
    sound.export(path_wav, format="wav")
    return

def pitch_shift_up(path_wav):
    # Elevar a frequência do áudio completo
    proc_path_wav = "proc.wav"
    s = Server(audio="offline").boot()
    filedur = sndinfo(path_wav)[1]
    s.recordOptions(dur=filedur, filename=proc_path_wav)
    ifile = SfPlayer(path_wav)
    FreqShift(ifile, shift=15, mul=1.0).out()
    s.start()
    return proc_path_wav

def pitch_recognition(path_wav):
    # crepe
    step_size = 10
    sr, audio = wavfile.read(path_wav)
    time, frequency, confidence, activation = crepe.predict(audio, sr, model_capacity='tiny', viterbi=True, step_size=step_size, verbose=1)
    #print(frequency)
    plt.plot(time, frequency)
    plt.plot(time, confidence*100, 'r')
    plt.xscale("linear")
    #plt.show()

    parts, time, frequency = identify_voice_parts(time, frequency, confidence)
    semitones = calc_average_frequency_voice_part(parts, time, frequency)
    #print(semitones)
    plt.plot(time, frequency)
    plt.plot(time, semitones, 'r')
    plt.xscale("linear")
    #plt.show()

    shift = []
    i = 0
    for f in frequency:
        if math.isnan(f):
            sft = 0
        else:
            sft = utils.octave_difference(semitones[i], f)
            #sft = utils.calc_pitch_shift(semitones[i], f)
        shift.append(sft)
        i = i + 1
    print(shift)
    separate_in_chunks(path_wav, shift, step_size)
    
    return
    #print(confidence)
    #print(activation)

    #for c in confidence:
    #    while c > 0.7:
    #        continue
    #semitones = [164.81, 587.33, 49.00]
    shift = []
    for f in frequency:
        if math.isnan(f):
            sft = 0
        else:
            sft = utils.calc_pitch_shift(f)
        shift.append(sft)
    print(shift)
    separate_in_chunks(path_wav, shift, step_size)
    return

def identify_voice_parts(time, frequency, confidence):
    #idx_part_start = []
    #idx_part_end = []
    parts = []

    i = 0
    idx_start = 0
    idx_end = 0
    for f in frequency:
        if confidence[i] > 0.60:
            if idx_start == 0:
                idx_start = i
        else:
            if idx_start != 0:
                idx_end = i
                #idx_part_start.append(idx_start)
                #idx_part_end.append(idx_start)
                parts.append([idx_start, idx_end])
                idx_start = 0
                idx_end = 0
        i = i + 1
    print(parts)
    print(len(parts))
    return parts, time, frequency

def calc_average_frequency_voice_part(parts, time, frequency):
    semitones = [0] * len(frequency)
    for p in parts:
        length = p[1] - p[0]
        average_freq = sum(frequency[p[0]:p[1]]) / length
        semitone = utils.find_nearest(utils.fundamentals, average_freq)
        #semitones.append(semitone)
        for i in range(p[0],p[1]):
            semitones[i] = semitone
    return semitones

def separate_in_chunks(path_wav, shift, step_size):
    # Separar o áudio em trechos e salvar numa pasta
    myaudio = AudioSegment.from_wav(path_wav)
    chunk_length_ms = step_size # pydub calculates in millisec
    chunks = make_chunks(myaudio, chunk_length_ms) #Make chunks of one sec

    chunks_dir = "chunks"
    if not os.path.exists(chunks_dir):
        os.mkdir(chunks_dir)

    #Export all of the individual chunks as wav files
    for i, chunk in enumerate(chunks):
        chunk_name = "chunk{0}.wav".format(i)
        chunks_path = os.path.join(chunks_dir, chunk_name)
        print("exporting " + chunks_path)
        chunk.export(chunks_path, format="wav")

    #time.sleep(5)
    for i, chunk in enumerate(chunks):
        chunk_name = "chunk{0}.wav".format(i)
        chunks_path = os.path.join(chunks_dir, chunk_name)
        proc_chunk_name = "proc_" + chunk_name
        proc_chunk_path  = os.path.join(chunks_dir, proc_chunk_name)
        #pitch_correction(chunks_path, proc_chunk_path, shift[i])
        utils.pitch_modulation_chunk(chunks_path, proc_chunk_path, shift[i])
       
    return

# def pitch_correction(chunk_path, proc_chunk_path, shift):
#     # Correção do pitch de cada chunk para o semitom mais próximo
#     s = Server(audio="offline").boot()
#     filedur = sndinfo(chunk_path)[1]
#     s.recordOptions(dur=filedur, filename=proc_chunk_path)
#     sf = SfPlayer(chunk_path)
#     b = FreqShift(sf, shift=shift, mul=1.0).out(0)
#     s.start()
#     return

def pitch_correction(chunk_path, proc_chunk_path, shift):
    # Correção do pitch de cada chunk para o semitom mais próximo
    
    return

def reunite_chunks():
    # Reunir todos os chunks em um arquivo de áudio
    prefixed = [filename for filename in os.listdir('chunks') if filename.startswith("proc_")]
    prefixed = utils.sort_nicely(prefixed)

    combined = AudioSegment.from_file("chunks/proc_chunk0.wav", format="wav")

    first = True
    for p in prefixed:
        if first == True:
            first = False
        else:
            print(p)
            sound = AudioSegment.from_file("chunks/" + p, format="wav")
            combined = combined + sound

    # simple export
    file_handle = combined.export("chunks/output.wav", format="wav")
    return

def add_echo_effect(path):
    s = Server().boot()
    # stereo playback with a slight shift between the two channels.
    sf = SfPlayer(path, speed=[1, 1], loop=True, mul=1.0).out()
    a = FreqShift(sf, shift=15, mul=0.6)
    b = FreqShift(sf, shift=25, mul=0.3)#.out()
    harm = Harmonizer(b, transpo=1.2, winsize=0.02, feedback=0.02, mul=0.5).out()
    s.gui(locals())
    return

def main():
    #s = Server().boot()
    #s.start()
    path_mp3 = "download.mp3"
    path_wav = "download.wav"
    pitch_recognition(path_wav)
    reunite_chunks()
    #add_echo_effect("chunks\output.wav")

    #utils.pitch_modulation()
    #utils.pitch_modulation_pydub()

    #text = "It's been a long time. How have you been?"
    #mp3_link = request_tts(text)
    #if mp3_link != "":
        #download_mp3(mp3_link, path_mp3)
        #convert_mp3_to_wav()
    #else:
    #    print("Error")

    #convert_mp3_to_wav(path_mp3, path_wav)
    #path_wav = pitch_shift_up(path_wav)
    #pitch_recognition(path_wav)
    #reunite_chunks()
    #path_wav = pitch_shift_up(path_wav)
    #separate_in_chunks(path)
    #s.gui(locals())
    return

if __name__ == "__main__":
    main()