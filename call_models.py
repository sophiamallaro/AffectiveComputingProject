from dimensional import get_dimensional_emotion
from getUserSongs import *
from Basic_Emotions_combine import *
from titles import *
import math
import torch
import lib 
import json
from pprint import pprint

def get_va_scores(dictionary, text_va_scores, alpha_arousal = 0.5, alpha_valence = 0.5):
    audio_va_scores = get_dimensional_emotion(dictionary)
    dimensional_dictionary = {}
    for song_id, audio_va_score in audio_va_scores.items():
        if song_id in text_va_scores.keys():
            dimensional_dictionary[song_id] = { "text_arousal"  : text_va_scores[song_id]["Arousal"], 
                                                "text_valence"  : text_va_scores[song_id]["Valence"], 
                                                "audio_arousal" : audio_va_score["arousal"],
                                                "audio_valence" : audio_va_score["valence"],
                                                "arousal"       : alpha_arousal * text_va_scores[song_id]["Arousal"] + (1 - alpha_arousal) * audio_va_score["arousal"],
                                                "valence"       : alpha_arousal * text_va_scores[song_id]["Valence"] + (1 - alpha_arousal) * audio_va_score["valence"]}
        else:
            dimensional_dictionary[song_id] = { "audio_arousal" : audio_va_score["arousal"],
                                                "audio_valence" : audio_va_score["valence"],
                                                "arousal"       : audio_va_score["arousal"],
                                                "valence"       : audio_va_score["valence"]}
    return dimensional_dictionary 

def generate_playlist_va(dimensional_dictionary, user_valence, user_arousal, min_dist = 0.1):
    song_list = []
    for song_id, va_dict in dimensional_dictionary.items():
        valence = va_dict["valence"]
        arousal = va_dict["arousal"]
        temp = math.sqrt( (valence - user_valence)**2 + (arousal - user_arousal)**2 )
        if(temp < min_dist):
            song_list.append(song_id)
    print(song_list)
    # make_playlist("Valence-Arousal", song_list)
    
def generate_playlist_be(user_basic_emotion): 
    song_list = get_recomendations(user_basic_emotion)
    make_playlist("Basic Emotions Playlist", song_list)

def get_emotions_audio(mp3folder, model):
    #mp3file = "data/" + k + ".mp3"
    ID = get_dictionary()
    #print (ID)
    songs_emo = {}
    for k, v in ID.items():
        mp3file = mp3folder +"/" + k + '.mp3'
        spec = lib.audio_read(mp3file)# extract spectrogram 
        spec = np.expand_dims(spec, axis=0)
        spec = np.expand_dims(spec, axis=0)
        spec = torch.from_numpy(spec)
        pred = model(spec)
        pred = pred.data.numpy()
        pred = pred[0]
        high = max(pred)
        pred = [0 if i!=high else 1 for i in pred]
        pred = np.array(pred)
        songs_emo[k] = pred
        print(k)
    return songs_emo


if __name__ == "__main__":
    songs_dictionary = json.load(open("dictionary.json"))
    new_songs_dictionary = dict([(k,v) for k, v in list(songs_dictionary.items())[:2]])
    basic_text_scores, va_text_scores = get_text_scores(new_songs_dictionary)
    
    dimensional_dictionary = get_va_scores(new_songs_dictionary, va_text_scores)
    generate_playlist_va(dimensional_dictionary, .5, .5)

    # PATH = 'model/model.pth'
    # model = ConvNet(6)
    # model.load_state_dict(torch.load(PATH))
    # model.eval()
    # dic = get_emotions_audio('data', model)
    # print(dic)