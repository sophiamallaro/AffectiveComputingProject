import numpy as np
import librosa
from scipy import signal
import matplotlib.pyplot as plt

def chunk(incoming, n_chunk):
    input_length = incoming.shape[1]
    chunk_length = input_length // n_chunk
    outputs = []
    for i in range(incoming.shape[0]):
        for j in range(n_chunk):
            outputs.append(incoming[i, j*chunk_length:(j+1)*chunk_length, :])
    outputs = np.array(outputs)
    return outputs

def audio_read(f):
    y, sr = librosa.core.load(f, sr=22050)
    #d = librosa.core.get_duration(y=y, sr=sr)
    #S = np.abs(librosa.stft(y, n_fft=512))**2
    #chroma = librosa.feature.chroma_stft(S=S, sr=sr)
    #chroma = np.expand_dims(chroma, axis=0)
    nfft = 512;
    nperseg = 512;
    M = nfft/2 + 1;
    noverlap = ((M+1)*nperseg - len(y))/M;
    _, _, Zxx = signal.spectrogram(y, window='hamming', nperseg=nperseg, noverlap=noverlap, nfft=nfft, mode='complex')
    #Zxx, f, t,_ = plt.specgram(y, NFFT=nfft, Fs=1,
    #     window=np.hamming(nperseg), noverlap=noverlap, mode='psd', scale='dB')
    Zxx = Zxx[:,0:257]
    S = np.abs(10*Zxx)**2
    #S = np.abs(Zxx)**2
    return S

def positional_encoding(batch_size, n_pos, d_pos):
    # keep dim 0 for padding token position encoding zero vector
    position_enc = np.array([
        [pos / np.power(10000, 2 * (j // 2) / d_pos) for j in range(d_pos)]
        if pos != 0 else np.zeros(d_pos) for pos in range(n_pos)])

    position_enc[1:, 0::2] = np.sin(position_enc[1:, 0::2]) # dim 2i
    position_enc[1:, 1::2] = np.cos(position_enc[1:, 1::2]) # dim 2i+1
    position_enc = np.tile(position_enc, [batch_size, 1, 1])
    return position_enc

def get_rec(user_emo ,songs_emo=songs_emo):
    high = max(user_emo)
    normal = [0 if i!=high else 1 for i in user_emo]
    normal = np.array(normal)
    #normaal = max (user_emo)
    song_ids = []
    for k,v in songs_emo.items():
        score = np.dot(normal, v)
        if score > 0:
            song_ids.append(k)
    return song_ids

def emotion_analyzer(text,emotion_dict=emotion_dict):
    #Set up the result dictionary
    emotions = {x for y in emotion_dict.values() for x in y}
    emotion_count = dict()
    for emotion in emotions:
        emotion_count[emotion] = 0

    words = []
    total_words = len(text.split())
    for word in text.split():
        if emotion_dict.get(word):
            words.append(word)
            for emotion in emotion_dict.get(word):
                emotion_count[emotion] += 1
    for e in emotions:
        emotion_count[e] = emotion_count[e]/len(words)
    total = emotion_count['anger']+emotion_count['disgust']+emotion_count['fear']+emotion_count['joy']+emotion_count['sadness']+emotion_count['anticipation']
    vector = [emotion_count['anger']/total, emotion_count['anticipation']/total, emotion_count['disgust']/total, emotion_count['fear']/total, emotion_count['joy']/total, emotion_count['sadness']/total]
    return vector