import dimensional
from dimensional import *
from getUserSongs import *
import lyricsgenius as genius
from Basic_Emotions_combine import *
from titles import *
import math
import torch
import lib 

def get_scores_text():
    basic, va = get_text_scores(get_dictionary())
    print("BASIC SCORES")
    print(basic)
    print("VA")
    print(va)


def get_valence_scores():
    va_dictionary = get_dimensional_emotion()
    return va_dictionary

def generate_playlist_va(result, user_val, user_arousal):
    song_list = []
    for key, value in result.items():
        x = value["valence"]
        y = value["arousal"]
        temp = math.sqrt( (x - user_val)**2 + (y - user_arousal)**2 )
        if(temp < 0.5):
            song_list.append(key)
    make_playlist("Valence-Arousal", song_list)
    
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
    #va_scores = get_valence_scores()
    #generate_playlist_va(va_scores, .5, .5)
    #get_scores_text()
    PATH = 'model/model.pth'
    model = ConvNet(6)
    model.load_state_dict(torch.load(PATH))
    model.eval()
    dic = get_emotions_audio('data', model)
    print(dic)