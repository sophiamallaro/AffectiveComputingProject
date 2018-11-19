import os
import pickle
import numpy as np
import pandas as pd
import librosa as lr
from PyLyrics import PyLyrics
import lyricsgenius as genius
from collections import Counter

vad = "text/NRC-VAD-Lexicon.txt"
vad_df = pd.read_csv(vad, delimiter = "\t", index_col = 0)
arousal_model = pickle.load(open("dimensional/arousal_model.pkl", "rb"))
valence_model = pickle.load(open("dimensional/valence_model.pkl", "rb"))
scaling = pd.read_csv("dimensional/scaling.csv", index_col=0, header=0)
print("lexicon, models and scalings loaded for dimensional mer")

api = genius.Genius('9mXsJ6OfC-KdM2QF1xl_0hRVZ7KiqrQYtUwobdB4kcpVsClOHUGf_d1a8qQjfIoa')

if not os.path.exists("temp/"):
    os.makedirs("temp/")

def create_features(tracks_dictionary, songs_folder = "data/", temp_folder = "temp/", limit = -1, remove_temp = False):
    assert len(tracks_dictionary) > 0, "empty dictionary!"

    song_ids = []
    titles = []
    artists = []
    song_ids_with_lyrics = []
    
    for i, (song_id, (title, artist)) in enumerate(tracks_dictionary.items()): 
        found_features = False
        found_lyrics = False
        mp3_file_path = songs_folder + "{}.mp3".format(song_id)
        print("Song: {}, Artist: {}, id: {}".format(title, artist, song_id))

        try: 
            lyrics = PyLyrics.getLyrics(artist, title)
            print("lyrics extracted using pylyrics")
            with open(temp_folder + "temp_{}.txt".format(song_id), "w") as fout:
                fout.write(lyrics)
            found_lyrics = True
        except Exception:
            print("lyrics not found")

        if not found_lyrics:
            song = api.search_song(title, artist)
            if song is not None:
                print("lyrics extracted using lyricsgenius")
                lyrics = song.lyrics
                with open(temp_folder + "temp_{}.txt".format(song_id), "w") as fout:
                    fout.write(lyrics)
                found_lyrics = True

        if os.path.exists(mp3_file_path):
            y, sr = lr.core.load(mp3_file_path, sr = None)
            wav_file_path = temp_folder + "temp_{}.wav".format(song_id)
            lr.output.write_wav(wav_file_path, y, sr)
            print("converted mp3 to wav")

            feature_file_path = temp_folder + "temp_features_{}.csv".format(song_id)
            os.system("opensmile/inst/bin/SMILExtract -noconsoleoutput -C dimensional/IS13_ComParE_lld-func.conf -I {} -O {}".format(wav_file_path, feature_file_path))
            print("features created")
            print()
            found_features = True
        else:
            print("mp3 not found")
        print()

        if found_features:
            song_ids.append(song_id)
            if found_lyrics:
               song_ids_with_lyrics.append(song_id)
            titles.append(title)
            artists.append(artist)

        if i == limit - 1:
            break

    columns = list(pd.read_csv(feature_file_path, delimiter = ";", index_col = 0, header = 0).columns)
    columns = [column for column in columns if column.endswith("_amean")]
    mean_columns = [column[:-6] + "_mean" for column in columns]
    std_columns = [column[:-6] + "_std" for column in columns]
    demo_df = pd.DataFrame(index = song_ids, columns = mean_columns + std_columns)

    for song_id in song_ids:
        feature_file_path = temp_folder + "temp_features_{}.csv".format(song_id)
        song_df = pd.read_csv(feature_file_path, delimiter = ";", index_col = 0, header = 0)
        demo_df.loc[song_id, mean_columns] = song_df[columns].mean().values.copy()
        demo_df.loc[song_id, std_columns] = song_df[columns].std().values.copy()
        print("done aggregating {}".format(song_id))
    print("features created for demo songs\n")
    demo_df.to_csv(temp_folder + "aggregate.csv")
    print()

    if remove_temp:
        print("removing temp files...", end = "")
        for song_id in song_ids:
            lyrics_file_path = temp_folder + "temp_{}.txt".format(song_id)
            wav_file_path = temp_folder + "temp_{}.wav".format(song_id)
            feature_file_path = temp_folder + "temp_features_{}.csv".format(song_id)
            os.system("rm {} {} {}".format(lyrics_file_path, wav_file_path, feature_file_path))
        print("done\n")

    emotion = pd.DataFrame(index = song_ids, columns = ["title","artist","lyrics","audio","text_arousal","text_valence","audio_arousal","audio_valence","arousal","valence"])
    emotion["title"] = titles
    emotion["artist"] = artists
    emotion.loc["lyrics"] = emotion.index.map(lambda song_id: temp_folder + "temp_{}.txt".format(song_id) if song_id in song_ids_with_lyrics else np.nan)
    emotion.loc["audio"] = emotion.index.map(lambda song_id: temp_folder + "temp_features_{}.csv".format(song_id))
    emotion.to_csv("emotion.csv")

    return emotion

def get_dimensional_emotion(emotion_df, alpha_arousal, alpha_valence):
    get_text_dimensional_emotion(emotion_df)
    get_audio_dimensional_emotion(emotion_df)

    no_lyrics_index = emotion_df["lyrics"].isna()
    lyrics_index = ~no_lyrics_index

    emotion_df.loc[lyrics_index, "arousal"] = alpha_arousal * emotion_df.loc[lyrics_index, "audio_arousal"] + (1 - alpha_arousal) * emotion_df.loc[lyrics_index, "text_arousal"]
    emotion_df.loc[lyrics_index, "valence"] = alpha_valence * emotion_df.loc[lyrics_index, "audio_valence"] + (1 - alpha_valence) * emotion_df.loc[lyrics_index, "text_valence"]
    
    emotion_df.loc[no_lyrics_index, "arousal"] = emotion_df.loc[no_lyrics_index, "audio_arousal"]
    emotion_df.loc[no_lyrics_index, "valence"] = emotion_df.loc[no_lyrics_index, "audio_valence"]
    
    emotion_df.to_csv("emotion.csv")
    return emotion_df

def get_text_dimensional_emotion(emotion_df):
    for song_id in emotion_df.index[emotion_df.lyrics.isna() == False]:
        file_path = emotion_df.lyrics[song_id]
        
        with open(file_path) as fin:
            lyrics = fin.read().strip()
        words = lyrics.split()
        
        n = len(words)
        freq_dist = Counter(words)
        prob = pd.Series(index = vad_df.index, data = 0)
        for word, freq in freq_dist.items():
            prob[prob.index == word] = freq/n
    
        valence = (vad_df.Valence * prob).sum()
        arousal = (vad_df.Arousal * prob).sum()
    
        emotion_df.loc[song_id, "text_arousal"] = arousal
        emotion_df.loc[song_id, "text_valence"] = valence
    print("text emotion calculated")
    
def get_audio_dimensional_emotion(emotion_df, temp_folder = "temp/"):
    aggregate_df = pd.read_csv(temp_folder + "aggregate.csv", index_col=0, header=0)
    aggregate_df_scaled = (aggregate_df - scaling["mean"])/scaling["std"]

    emotion_df["audio_arousal"] = (arousal_model.predict(aggregate_df_scaled) - 1)/8
    emotion_df["audio_valence"] = (valence_model.predict(aggregate_df_scaled) - 1)/8
    
    print("audio emotion calculated")

def get_emotion(tracks_dictionary, alpha_arousal = 0.5, alpha_valence = 0.5, songs_folder = "data/", temp_folder = "temp/", limit = -1, remove_temp = False):
    emotion = create_features(tracks_dictionary, songs_folder, temp_folder, limit, remove_temp)
    emotion = get_dimensional_emotion(emotion, alpha_arousal, alpha_valence)
    return emotion.transpose().to_dict()
