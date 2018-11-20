import dimensional
from dimensional import *
from getUserSongs import *
import lyricsgenius as genius
from Basic_Emotions_combine import *
import math

def generate_playlist_va(user_val, user_arousal):
    names = get_dictionary()
    result = dimensional.get_emotion(names)
    song_list = {}
    for key in result:
        x, y = result[key]
        temp = math.sqrt( (x - user_val)**2 + (y - user_arousal)**2 )
        if(temp < 2):
            song_list.append(key)
    make_playlist("Valence-Arousal", song_list)
    
def generate_playlist_be(user_basic_emotion): 
    song_list = get_recomendations(user_basic_emotion)
    make_playlist("Basic Emotions Playlist", song_list)
