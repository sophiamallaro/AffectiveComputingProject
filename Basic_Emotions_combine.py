from PyLyrics import *
import nltk
#import indicoio
import pandas as pd
import spotipy
import urllib
from spotipy.oauth2 import SpotifyClientCredentials
import numpy as np
import torch
# import lib
from ConvNet import ConvNet
from getUserSongs import *
import lyricsgenius as genius

def get_emotions_audio(mp3folder, model):
    #mp3file = "data/" + k + ".mp3"
    ID = get_dictionary()
    print (ID)
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
    return songs_emo



def get_song_emotions():
    api = genius.Genius('9mXsJ6OfC-KdM2QF1xl_0hRVZ7KiqrQYtUwobdB4kcpVsClOHUGf_d1a8qQjfIoa')
    emotion_dict = np.load('emotion_dict.npy')
    emotion_dict = emotion_dict.item()
    names = get_dictionary()

    PATH = "model/model.pth"
    num_classes = 6
    model = ConvNet(num_classes)
    model.load_state_dict(torch.load(PATH))
    model.eval()

    print("load models")

    songs_emo = {}
    for k,v in names.items():
        print(k,v)
        title = v[0]
        artist = v[1]
        text_emotions = [0 for i in range(6)]
        output = [0 for i in range(6)]
        pred = [0 for i in range(6)]
        try:
            lyrics = PyLyrics.getLyrics(artist, title)
            if lyrics == "":
                song = api.search_song(artist, title)
                lyrics = song.lyrics
            emovector = lib.emotion_analyzer(lyrics, emotion_dict)
            high = max(emovector)
        
            text_emotions = [0 if i!=high else 1 for i in emovector]
            text_emotions = np.array(text_emotions)
        except:
            print("passing")
        #try:
        mp3file = "data/" + k + ".mp3"

        spec = lib.audio_read(mp3file)# extract spectrogram
        spec = torch.from_numpy(spec)
        pred = model(spec)
        high = max(pred)
        pred = [0 if i!=high else 1 for i in pred]
        pred = np.array(pred)
        output = np.add(pred, text_emotions)
        np.clip(output,0,1,out=output)
        songs_emo[k] = output
        print('finishing '+k)

    return songs_emo

def get_recomendations(user_emotion):
    all_songs = get_song_emotions()
    ans = lib.get_rec(user_emotion,all_songs)
    return ans
