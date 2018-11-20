from dimensional import get_dimensional_emotion
from getUserSongs import *
from Basic_Emotions_combine import *
from titles import *
import math
import torch
import lib 
import json
from pprint import pprint

def generate_playlist_va(dictionary, user_valence, user_arousal, min_dist = 0.2):
    dimensional_dictionary = get_dimensional_emotion(dictionary)
    song_list = []
    for song_id, va_dict in dimensional_dictionary.items():
        valence = va_dict["valence"]
        arousal = va_dict["arousal"]
        temp = math.sqrt( (valence - user_valence)**2 + (arousal - user_arousal)**2 )
        if(temp < min_dist):
            song_list.append(song_id)
    # print(song_list)
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
    dictionary = json.load(open("dictionary.json"))
    new_dictionary = dict([(k,v) for k, v in list(dictionary.items())[:2]])
    generate_playlist_va(dictionary, .5, .5)
    # basic, va = get_text_scores(dictionary)
    # pprint(basic)
    # print()
    # pprint(va)

    # PATH = 'model/model.pth'
    # model = ConvNet(6)
    # model.load_state_dict(torch.load(PATH))
    # model.eval()
    # dic = get_emotions_audio('data', model)
    # print(dic)