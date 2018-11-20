import os
import pickle
import numpy as np
import pandas as pd
import pydub
from PyLyrics import PyLyrics
import lyricsgenius as genius
from collections import Counter

import json
from pprint import pprint

# vad = "text/NRC-VAD-Lexicon.txt"
# vad_df = pd.read_csv(vad, delimiter = "\t", index_col = 0)
arousal_model = pickle.load(open("dimensional/arousal_model.pkl", "rb"))
valence_model = pickle.load(open("dimensional/valence_model.pkl", "rb"))
scaling = pd.read_csv("dimensional/scaling.csv", index_col=0, header=0)
print("lexicon, models and scalings loaded for dimensional mer")

api = genius.Genius('9mXsJ6OfC-KdM2QF1xl_0hRVZ7KiqrQYtUwobdB4kcpVsClOHUGf_d1a8qQjfIoa')

if not os.path.exists("temp/"):
    os.makedirs("temp/")

def create_features(tracks_dictionary, songs_folder = "data/", temp_folder = "temp/", limit = -1, remove_temp = False):
    assert len(tracks_dictionary) > 0, "empty dictionary!"

    keys = tracks_dictionary.keys()
    song_ids = []
    
    for i, key in enumerate(keys): 
        found_features = False
        mp3_file_path = songs_folder + "{}.mp3".format(key)
        print("{}. id: {}".format(i + 1, key))

        if os.path.exists(mp3_file_path):
            mp3_file = pydub.AudioSegment.from_mp3(mp3_file_path)
            wav_file_path = temp_folder + "temp_{}.wav".format(key)
            mp3_file.export(wav_file_path, format="wav")
            print("converted mp3 to wav")

            feature_file_path = temp_folder + "temp_features_{}.csv".format(key)
            os.system("opensmile/inst/bin/SMILExtract -noconsoleoutput -C dimensional/IS13_ComParE_lld-func.conf -I {} -O {}".format(wav_file_path, feature_file_path))
            print("features created")
            print()
            found_features = True
        else:
            print("mp3 not found")
        print()

        if found_features:
            song_ids.append(key)

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
            wav_file_path = temp_folder + "temp_{}.wav".format(song_id)
            feature_file_path = temp_folder + "temp_features_{}.csv".format(song_id)
            os.system("rm {} {}".format(wav_file_path, feature_file_path))
        print("done\n")

    emotion = pd.DataFrame(index = song_ids, columns = ["arousal","valence"])
    emotion.to_csv("emotion.csv")

    return emotion
    
def get_audio_dimensional_emotion(emotion_df, temp_folder = "temp/"):
    aggregate_df = pd.read_csv(temp_folder + "aggregate.csv", index_col=0, header=0)
    aggregate_df_scaled = (aggregate_df - scaling["mean"])/scaling["std"]

    emotion_df["arousal"] = (arousal_model.predict(aggregate_df_scaled) - 1)/8
    emotion_df["valence"] = (valence_model.predict(aggregate_df_scaled) - 1)/8
    
    print("audio emotion calculated")
    return emotion_df

def get_emotion(tracks_dictionary, songs_folder = "data/", temp_folder = "temp/", limit = -1, remove_temp = False):
    emotion = create_features(tracks_dictionary, songs_folder, temp_folder, limit, remove_temp)
    emotion = get_audio_dimensional_emotion(emotion, temp_folder)
    return emotion.transpose().to_dict()

if __name__ == "__main__":
    dictionary = json.load(open("dictionary.json"))
    emotion = get_emotion(dictionary)
    pprint(emotion)
