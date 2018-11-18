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
for k,v in names.items():
    title = v[0]
    artist = v[1]
    text_emotions = [0 for i in range(6)]
    output = [0 for i in range(6)]
    pred = [0 for i in range(6)]
    try:
        lyrics = PyLyrics.getLyrics(artist, title)
        emovector = lib.emotion_analyzer(lyrics, emotion_dict)
        high = max(emovector)
        
        text_emotions = [0 if i!=high else 1 for i in emovector]
        text_emotions = np.array(text_emotions)
    except:
        pass
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
    


# In[5]:




        


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




