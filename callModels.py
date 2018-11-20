import dimensional
from dimensional import *
from getUserSongs import *
import lyricsgenius as genius
from Basic_Emotions_combine import *
import math

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

if __name__ == "__main__":
    va_scores = get_valence_scores()
    generate_playlist_va(va_scores, .5, .5)