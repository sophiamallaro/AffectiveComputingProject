from dimensional import get_dimensional_emotion
# from getUserSongs import *
# from Basic_Emotions_combine import get_recomendations
# from titles import get_text_scores
import math
import torch
import lib 
import json
from pprint import pprint
from ConvNet import ConvNet
import numpy as np
import torch

def get_va_scores(dictionary, text_va_scores, alpha_arousal = 0.5, alpha_valence = 0.5, data = "data/"):
    audio_va_scores = get_dimensional_emotion(dictionary, songs_folder=data)
    dimensional_dictionary = {}
    for song_id in dictionary.keys():
        flag = False
        if song_id in text_va_scores.keys() and song_id in audio_va_scores.keys():
            arousal = alpha_arousal * text_va_scores[song_id]["Arousal"] + (1 - alpha_arousal) * audio_va_scores[song_id]["arousal"]
            valence = alpha_valence * text_va_scores[song_id]["Valence"] + (1 - alpha_valence) * audio_va_scores[song_id]["valence"]
            flag = True
        elif song_id in text_va_scores.keys() and song_id not in audio_va_scores.keys():
            arousal = text_va_scores[song_id]["Arousal"]
            valence = text_va_scores[song_id]["Valence"]
            flag = True
        elif song_id not in text_va_scores.keys() and song_id in audio_va_scores.keys():
            arousal = audio_va_scores[song_id]["arousal"]
            valence = audio_va_scores[song_id]["valence"]
            flag = True
        if flag:
            dimensional_dictionary[song_id] = {"arousal": arousal, "valence": valence}
    return dimensional_dictionary 

def generate_playlist_va(dimensional_dictionary, user_valence, user_arousal, min_dist = 0.1):
    song_list = []
    for song_id, va_dict in dimensional_dictionary.items():
        valence = va_dict["valence"]
        arousal = va_dict["arousal"]
        temp = math.sqrt( (valence - user_valence)**2 + (arousal - user_arousal)**2 )
        if(temp < min_dist):
            song_list.append(song_id)
    return song_list
    
def generate_playlist_be(user_basic_emotion, library): 
    song_list = lib.get_rec(user_basic_emotion, library)
    # make_playlist("Basic Emotions Playlist", song_list)
    return song_list
def get_basic_audio(mp3folder, model, dictionary):
    #mp3file = "data/" + k + ".mp3"
    #ID = get_dictionary()
    #print (ID)
    songs_emo = {}
    for k, v in dictionary.items():
        try: 
            mp3file = mp3folder +"/" + k + '.mp3'
            spec = lib.audio_read(mp3file)# extract spectrogram 
            spec = np.expand_dims(spec, axis=0)
            spec = np.expand_dims(spec, axis=0)
            spec = torch.from_numpy(spec)
            pred = model(spec)
            pred = pred.data.numpy()
            pred = pred[0]
            pred = np.array(pred)
            songs_emo[k] = pred
            print(k)
        except:
            print("don't have mp3:"+k)

    return songs_emo

def get_basic_combine(mp3path, dictionary, basic_text_scores):
    PATH = 'model/model.pth'
    model = ConvNet(6)
    model.load_state_dict(torch.load(PATH))
    model.eval()
    basic_audio_scores = get_basic_audio(mp3path, model, dictionary)
    basic_combine_score = {}

    for k, _ in dictionary.items():
        if k in basic_text_scores.keys() and k in basic_audio_scores.keys():
            score = np.add(basic_text_scores[k], 0.1*basic_audio_scores[k])
            high = max(score)
            max_output = [0 if i!=high else 1 for i in score]
            max_output = np.array(max_output)
            np.clip(max_output,0,1,out=max_output)
            basic_combine_score[k] = max_output

        elif k in basic_text_scores.keys() and k not in basic_audio_scores.keys():
            score = basic_text_scores[k]
            high = max(score)
            max_output = [0 if i!=high else 1 for i in score]
            max_output = np.array(max_output)
            np.clip(max_output,0,1,out=max_output)
            basic_combine_score[k] = max_output

        elif k not in basic_text_scores.keys() and k in basic_audio_scores.keys():
            score = basic_audio_scores[k]
            high = max(score)
            max_output = [0 if i!=high else 1 for i in score]
            max_output = np.array(max_output)
            np.clip(max_output,0,1,out=max_output)
            basic_combine_score[k] = max_output


    return basic_combine_score