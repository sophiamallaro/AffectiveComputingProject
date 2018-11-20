import lyricsgenius as genius
from PyLyrics import *
import nltk
import indicoio
import pandas as pd
import spotipy
import urllib
import getUserSongs
from spotipy.oauth2 import SpotifyClientCredentials

def get_text_scores(dictionary):
    api = genius.Genius('9mXsJ6OfC-KdM2QF1xl_0hRVZ7KiqrQYtUwobdB4kcpVsClOHUGf_d1a8qQjfIoa')
    nrc = "text/NRC-emotion-lexicon-wordlevel-alphabetized-v0.92.txt"
    count=0
    emotion_dict=dict()
    with open(nrc,'r') as f:
        all_lines = list()
        for line in f:
            if count < 46:
                count+=1
                continue
            line = line.strip().split('\t')
            if int(line[2]) == 1:
                if emotion_dict.get(line[0]):
                    emotion_dict[line[0]].append(line[1])
                else:
                    emotion_dict[line[0]] = [line[1]]


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


    def get_basic(dictionary):
        badsongs =[]
        basic = {}
        for k, track in dictionary.items():
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
            lyrics = ""
            try:
                lyrics = PyLyrics.getLyrics(artist_str , title)
                basic[k] = emotion_analyzer(lyrics,emotion_dict)
            except:
                print("No Lyrics Found.")
            try:
                #print (lyrics)
                if lyrics == "":
                    song = api.search_song(title.lower(), artists[0])
                    lyrics = song.lyrics
                    basic[k] = emotion_analyzer(lyrics,emotion_dict)
            except:
                print("Seriously.")
            try:
                if lyrics == "" and len(artists) >= 2:
                    artist_str = ' & '. join(str(x) for x in artists[:2])
                    print(artist_str)
                    lyrics = PyLyrics.getLyrics(artist_str.lower(),title.lower())
                    lyrics = song.lyrics
                    print(lyrics)
                    basic[k] = emotion_analyzer(lyrics,emotion_dict)
            except:
                print("Nope.")
            try:
                if lyrics == "" and len(artists) >= 2:
                    artist_str = ' and '. join(str(x) for x in artists[:2])
                    print(artist_str.lower().capitalize())
                    lyrics = api.search_song(title.lower(),artist_str.lower().capitalize())
                    lyrics = song.lyrics
                    print(lyrics)
                    basic[k] = emotion_analyzer(lyrics,emotion_dict)
            except:
                print('Bye.')
                badsongs.append(k)
        return basic

    vad = "text/NRC-VAD-Lexicon.txt"
    data = pd.read_csv(vad, delimiter = "\t")

    def VAD_analyzer(text, data=data):
        #Set up the result dictionary
        emotions = list(data)[1:]
        emotion_count = dict()
        for emotion in emotions:
            emotion_count[emotion] = 0
        words = []
        total_words = len(text.split())
        for word in text.split():
            row = data.loc[data['Word'] == word]
            if not row.empty:
                words.append(word)
                for emotion in emotions:
                    emotion_count[emotion] += row[emotion].iloc[0]
        for e in emotions:
            emotion_count[e] = emotion_count[e]/len(words)

        return emotion_count

    def get_VAD(dictionary):
        badsongs =[]
        vad = {}
        for k, track in dictionary.items():
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
            lyrics = ""
            try:
                lyrics = PyLyrics.getLyrics(artist_str , title)
                vad[k] = VAD_analyzer(lyrics)
            except:
                print("No Lyrics Found.")
            try:
                #print (lyrics)
                if lyrics == "":
                    song = api.search_song(title.lower(), artists[0])
                    lyrics = song.lyrics
                    vad[k] = VAD_analyzer(lyrics)
                    print(vad[k])
            except:
                print("Seriously.")
            try:
                if lyrics == "" and len(artists) >= 2:
                    artist_str = ' & '. join(str(x) for x in artists[:2])
                    print(artist_str)
                    lyrics = PyLyrics.getLyrics(artist_str.lower(),title.lower())
                    lyrics = song.lyrics
                    #print(lyrics)
                    vad[k] = VAD_analyzer(lyrics)
            except:
                print("Nope.")
            try:
                if lyrics == "" and len(artists) >= 2:
                    artist_str = ' and '. join(str(x) for x in artists[:2])
                    print(artist_str.lower().capitalize())
                    lyrics = api.search_song(title.lower(),artist_str.lower().capitalize())
                    lyrics = song.lyrics
                    #print(lyrics)
                    vad[k] = VAD_analyzer(lyrics)
            except:
                print('Bye.')
                badsongs.append(k)
        return vad


    basic = get_basic(dictionary)
    vad = get_VAD(dictionary)
    return basic, vad

