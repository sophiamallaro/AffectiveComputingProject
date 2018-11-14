import os
import pickle
import pandas as pd
from pydub import AudioSegment
from PyLyrics import PyLyrics
from collections import Counter

vad = "text/NRC-VAD-Lexicon.txt"
vad_df = pd.read_csv(vad, delimiter = "\t", index_col = 0)
arousal_model = pickle.load(open("dimensional/arousal_model.pkl", "rb"))
valence_model = pickle.load(open("dimensional/valence_model.pkl", "rb"))
print("lexicon and models loaded for dimensional mer")

def get_dimensional_emotion(mp3_file_paths, artists, titles):
    list_lyrics = []
    song_ids = []
    for i, (mp3_file_path, artist, title) in enumerate(zip(mp3_file_paths, artists, titles)): 
        song_id = i + 1
        try: 
            lyrics = PyLyrics.getLyrics(artist, title)
            print("lyrics extracted for song: {} by artist: {}".format(title, artist))
        except Exception as e:
            print("Error [ {} ] occured while trying to get lyrics for song: {} by artist: {}".format(e, title, artist))
            lyrics = ""
        list_lyrics.append(lyrics)
        song_ids.append(song_id)

        mp3_file = AudioSegment.from_mp3(mp3_file_path)
        wav_file_path = "temp/temp_{}.wav".format(song_id)
        mp3_file.export(wav_file_path, format="wav")
        print("converted {} to {}".format(mp3_file_path, wav_file_path))

        feature_file_path = "temp/temp_features_{}.csv".format(song_id)
        os.system("opensmile/inst/bin/SMILExtract -C dimensional/IS13_ComParE_lld-func.conf -I {} -O {}".format(wav_file_path, feature_file_path))
        print("features created in {}".format(feature_file_path))
        print()

    columns = list(pd.read_csv("temp/temp_features_1.csv", delimiter = ";", index_col = 0, header = 0).columns)
    columns = [column for column in columns if column.endswith("_amean")]
    mean_columns = [column[:-6] + "_mean" for column in columns]
    std_columns = [column[:-6] + "_std" for column in columns]
    demo_df = pd.DataFrame(index = song_ids, columns = mean_columns + std_columns)

    for song_id in song_ids:
        feature_file_path = "temp/temp_features_{}.csv".format(song_id)
        song_df = pd.read_csv(feature_file_path, delimiter = ";", index_col = 0, header = 0)
        demo_df.loc[song_id, mean_columns] = song_df[columns].mean().values
        demo_df.loc[song_id, std_columns] = song_df[columns].std().values
        print("done aggregating {}".format(feature_file_path))
    print("features created for demo songs\n")

    print("removing temp files...", end = "")
    for song_id in song_ids:
        wav_file_path = "temp/temp_{}.wav".format(song_id)
        feature_file_path = "temp/temp_features_{}.csv".format(song_id)
        os.system("rm {} {}".format(wav_file_path, feature_file_path))
    print("done")

    text_emotion = get_text_dimensional_emotion(song_ids, list_lyrics)
    print("text emotion calculated")
    audio_emotion = get_audio_dimensional_emotion(demo_df)
    print("audio emotion calculated")

    valence = (text_emotion["text_valence"] + audio_emotion["audio_valence"])/2
    arousal = (text_emotion["text_arousal"] + audio_emotion["audio_arousal"])/2

    return valence, arousal

def get_text_dimensional_emotion(song_ids, list_lyrics):
    text_emotion = pd.DataFrame(index = song_ids, columns = ["text_arousal","text_valence"])
    for song_id, lyrics in zip(song_ids, list_lyrics):
        words = lyrics.split()
        n = len(words)
        freq_dist = Counter(words)
        prob = pd.Series(index = vad_df.index, data = 0)
        for word, freq in freq_dist.items():
            prob[prob.index == word] = freq/n
        valence = (vad_df.Valence * prob).sum()
        arousal = (vad_df.Arousal * prob).sum()
        text_emotion.loc[song_id, "text_arousal"] = arousal
        text_emotion.loc[song_id, "text_valence"] = valence
    return text_emotion
    
def get_audio_dimensional_emotion(demo_df):
    arousal = arousal_model.predict(demo_df)
    valence = valence_model.predict(demo_df)
    audio_emotion = pd.DataFrame(columns = ["audio_arousal", "audio_valence"], index = demo_df.index)
    audio_emotion["audio_arousal"] = arousal
    audio_emotion["audio_valence"] = valence
    return audio_emotion