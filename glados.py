from pyo import *
import requests
from pydub import AudioSegment
from pydub.utils import make_chunks
import crepe
from scipy.io import wavfile
import matplotlib.pyplot as plt
import utils
import constants
import time

def request_tts(text):
    """ Faz uma requisição GET com texto desejado para gerar o áudio
    """
    data = {
        'msg': text,
        'lang': 'Kimberly', 
        'source': 'ttsmp3' 
    }
    response = requests.post('https://ttsmp3.com/makemp3_new.php', data=data)
    res = response.json()
    mp3_link = ""
    if 'MP3' in res:
        mp3_link = res['MP3']
    return mp3_link

def download_mp3(mp3_link, path):
    """ Faz o download do arquivo mp3
    """
    query = {
        'mp3': mp3_link,
        'location': 'direct'
    }
    response = requests.get('https://ttsmp3.com/dlmp3.php', params=query)
    with open(path, 'wb') as file:
        file.write(response.content)
    return

def convert_mp3_to_wav(path_mp3, path_wav):
    """ Converte mp3 para wav
    """
    sound = AudioSegment.from_mp3(path_mp3)
    sound.export(path_wav, format="wav")
    return

def pitch_recognition(path_wav):
    """ Utiliza a biblioteca CREPE para estimar as frequências de pitch do áudio
    """
    step_size = 10
    sr, audio = wavfile.read(path_wav)
    time, frequency, confidence, activation = crepe.predict(audio, sr, model_capacity='tiny', viterbi=True, step_size=step_size, verbose=1)
    
    plt.plot(time, frequency)
    plt.plot(time, confidence*100, 'r')
    plt.xscale("linear")
    #plt.show()

    parts, time, frequency = identify_voice_parts(time, frequency, confidence)
    semitones = calc_average_frequency_voice_part(parts, time, frequency)
    
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
            sft = utils.octave_difference(f, semitones[i])
        shift.append(sft)
        i = i + 1
    separate_in_chunks(path_wav, shift, step_size)
    return

def identify_voice_parts(time, frequency, confidence):
    """ Identifica quando a voz está sendo reproduzida, para dividir em
        trechos, de modo a calcular a frequência média de cada trecho
    """
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
                parts.append([idx_start, idx_end])
                idx_start = 0
                idx_end = 0
        i = i + 1
    return parts, time, frequency

def calc_average_frequency_voice_part(parts, time, frequency):
    """ Calcula a frequência média de cada trecho
    """
    semitones = [0] * len(frequency)
    for p in parts:
        length = p[1] - p[0]
        average_freq = sum(frequency[p[0]:p[1]]) / length
        semitone = utils.find_nearest(constants.FUNDAMENTALS, average_freq)
        for i in range(p[0],p[1]):
            semitones[i] = semitone
    return semitones

def separate_in_chunks(path_wav, shift, step_size):
    """ Separa o áudio em trechos e salva numa pasta
    """
    myaudio = AudioSegment.from_wav(path_wav)
    chunk_length_ms = step_size # pydub calculates in millisec
    chunks = make_chunks(myaudio, chunk_length_ms) # Make chunks of one sec

    chunks_dir = "chunks"
    if not os.path.exists(chunks_dir):
        os.mkdir(chunks_dir)

    # Export all of the individual chunks as wav files
    for i, chunk in enumerate(chunks):
        chunk_name = "chunk{0}.wav".format(i)
        chunks_path = os.path.join(chunks_dir, chunk_name)
        #print("exporting " + chunks_path)
        chunk.export(chunks_path, format="wav")

    for i, chunk in enumerate(chunks):
        chunk_name = "chunk{0}.wav".format(i)
        chunks_path = os.path.join(chunks_dir, chunk_name)
        proc_chunk_name = "proc_" + chunk_name
        proc_chunk_path  = os.path.join(chunks_dir, proc_chunk_name)
        utils.pitch_modulation_chunk(chunks_path, proc_chunk_path, shift[i])
    return

def reunite_chunks():
    """ Reune todos os chunks em um arquivo de áudio
    """
    prefixed = [filename for filename in os.listdir('chunks') if filename.startswith("proc_")]
    prefixed = utils.sort_nicely(prefixed)

    combined = AudioSegment.from_file("chunks/proc_chunk0.wav", format="wav")
    os.remove("chunks/proc_chunk0.wav")

    first = True
    for p in prefixed:
        if first == True:
            first = False
        else:
            #print(p)
            sound = AudioSegment.from_file("chunks/" + p, format="wav")
            combined = combined + sound
            os.remove("chunks/" + p)

    # simple export
    file_handle = combined.export("chunks/output.wav", format="wav")
    return

def add_echo_effect(path_out_wav):
    """ Adiciona efeito de eco na voz
    """
    s = Server().boot()
    # stereo playback with a slight shift between the two channels.
    sf = SfPlayer(path_out_wav, speed=[1, 0.999], loop=True, mul=1.0).out()
    harm = Harmonizer(sf, transpo=0.9, winsize=0.01, feedback=0.01, mul=0.1).out()
    s.gui(locals())
    return

def play(path_out_wav):
    """ Toca o áudio
    """
    s = Server().boot()
    sf = SfPlayer(path_out_wav, speed=[1, 1], loop=True, mul=1.0).out()
    s.gui(locals())
    return

def say(text):
    start_time = time.time()
    
    path_mp3 = "download.mp3"
    path_wav = "download.wav"
    path_out_wav = "chunks/output.wav"

    download = True
    modulate = True
    addEchoOrJustPlay = False

    if download == True:
        mp3_link = request_tts(text)
        if mp3_link != "":
            download_mp3(mp3_link, path_mp3)
            convert_mp3_to_wav(path_mp3, path_wav)
        else:
            print("Error")
    
    if modulate == True:
        pitch_recognition(path_wav)
        reunite_chunks()
    print("--- %s seconds ---" % (time.time() - start_time))
    if addEchoOrJustPlay == False:
        add_echo_effect(path_out_wav)
    else:
        play(path_out_wav)
    return

def main():
    start_time = time.time()
    
    path_mp3 = "download.mp3"
    path_wav = "download.wav"
    path_out_wav = "chunks/output.wav"

    download = False
    modulate = True
    addEchoOrJustPlay = False

    if download == True:
        text = "Hello and, again, welcome to the Aperture Science computer-aided enrichment center. We hope your brief detention in the relaxation vault has been a pleasant one. Your specimen has been processed and we are now ready to begin the test proper."
        mp3_link = request_tts(text)
        if mp3_link != "":
            download_mp3(mp3_link, path_mp3)
            convert_mp3_to_wav(path_mp3, path_wav)
        else:
            print("Error")
    
    if modulate == True:
        pitch_recognition(path_wav)
        reunite_chunks()
    print("--- %s seconds ---" % (time.time() - start_time))
    if addEchoOrJustPlay == False:
        add_echo_effect(path_out_wav)
    else:
        play(path_out_wav)
    return

if __name__ == "__main__":
    main()