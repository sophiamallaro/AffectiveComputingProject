from os import listdir
import numpy as np
import csv

def get_arrays(include_time = False):
    data_directory = "./data/deam/features_arrays/"
    files = listdir(data_directory)

    arrays = []
    ids = []

    for file in files:
        array = np.load(data_directory + file)[1:,:]
        if not include_time:
            array = array[:,1:]
        id_ = int(file.split(".")[0])
        arrays.append(array)
        ids.append(id_)

    return arrays, ids

def get_static_annotations():
    reader1 = csv.reader(open("data/deam/annotations/annotations averaged per song/song_level/static_annotations_averaged_songs_1_2000.csv"))
    reader2 = csv.reader(open("data/deam/annotations/annotations averaged per song/song_level/static_annotations_averaged_songs_2000_2058.csv"))

    next(reader1)
    next(reader2)
    id_to_annotation = {}

    for row in reader1:
        _id = int(row[0])
        valence = float(row[1])
        arousal = float(row[3])
        id_to_annotation[_id] = {"valence": valence, "arousal": arousal}

    for row in reader2:
        _id = int(row[0])
        valence = float(row[1])
        arousal = float(row[7])
        id_to_annotation[_id] = {"valence": valence, "arousal": arousal}

    return id_to_annotation
