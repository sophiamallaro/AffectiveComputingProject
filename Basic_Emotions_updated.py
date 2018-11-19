#!/usr/bin/env python
# coding: utf-8

# In[1]:


from PyLyrics import *
import nltk
#import indicoio
import pandas as pd
import spotipy
import urllib
from spotipy.oauth2 import SpotifyClientCredentials
import numpy as np
import torch
import lib
from ConvNet import ConvNet


# In[2]:


emotion_dict = np.load('emotion_dict.npy')
emotion_dict = emotion_dict.item() 
names = np.load('songs.npy')
names = names.item()


# In[3]:


PATH = "model/model.pth"
num_classes = 6
model = ConvNet(num_classes)
model.load_state_dict(torch.load(PATH))
model.eval()


# In[4]:



songs_emo = {}
for k,track in names.items():
    punct = ""
    for c in track[0]:
        if c in ['-', '!', '?', '(']:
            punct = c
    idx = track[0].find(punct)
    print(idx)
    if idx == 0:
        title = track[0]
    else:
        title = track[0][:idx-1]
    artists = []
    #print(track)
    for a in track[1]:        
        artists.append(a['name'])
    artist_str = ' & '.join(str(x) for x in artists) 
    print(title, artist_str)
    lyrics = ""
    try:
        lyrics = PyLyrics.getLyrics(artist_str , title)
        emovector = lib.emotion_analyzer(lyrics, emotion_dict)
        high = max(emovector)
        
        text_emotions = [0 if i!=high else 1 for i in emovector]
        text_emotions = np.array(text_emotions)
    except:
        print("No Lyrics Found.")
    try:
        #print (lyrics)
        if lyrics == "":
            song = api.search_song(title.lower(), artists[0])
            lyrics = song.lyrics
            emovector = lib.emotion_analyzer(lyrics, emotion_dict)
            high = max(emovector)
        
            text_emotions = [0 if i!=high else 1 for i in emovector]
            text_emotions = np.array(text_emotions)
    except:
        print("Seriously.")
    try:
        if lyrics == "" and len(artists) >= 2:
            artist_str = ' & '. join(str(x) for x in artists[:2])
            print(artist_str)
            lyrics = PyLyrics.getLyrics(artist_reformat.lower(),title.lower())
            lyrics = song.lyrics
            print(lyrics)
            emovector = lib.emotion_analyzer(lyrics, emotion_dict)
            high = max(emovector)
        
            text_emotions = [0 if i!=high else 1 for i in emovector]
            text_emotions = np.array(text_emotions)
    except:
        print("Nope.")
    try:
        if lyrics == "" and len(artists) >= 2:
            artist_str = ' and '. join(str(x) for x in artists[:2])
            print(artist_str.lower().capitalize())
            lyrics = api.search_song(title.lower(),artist_str.lower().capitalize())
            lyrics = song.lyrics
            emovector = lib.emotion_analyzer(lyrics, emotion_dict)
            high = max(emovector)
        
            text_emotions = [0 if i!=high else 1 for i in emovector]
            text_emotions = np.array(text_emotions)
    except:
        print('Bye.')
        badsongs.append(title)
    try:
        mp3file = "data/" + k + ".mp3"
        
        spec = lib.audio_read(mp3file)# extract spectrogram 
        pred = model(spec)
        high = max(pred)
        pred = [0 if i!=high else 1 for i in pred]
        pred = np.array(pred)
    except:
        pass

        
    output = np.add(pred, text_emotions)
    np.clip(output,0,1,out=output)
    songs_emo[k] = output
    print('finishing '+k)

print("Bad Songs:", badsongs)  


# In[5]:

def parse_text(dictionary):
    


        


# In[8]:


ans = lib.get_rec([0,0,0,0,1,1])


# In[9]:


ans


# In[11]:





# In[13]:


from getUserSongs import *
sp = generate_token()
make_playlist(sp, "sad", ans)


# In[15]:





# In[ ]:




