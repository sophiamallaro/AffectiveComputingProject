from os import listdir
import csv
import numpy as np

data_directory = "./data/deam/features/"
output_directory = "./data/deam/features_arrays/"

files = listdir(data_directory)
for file in files:
    id_ = file.split(".")[0]
    array = np.genfromtxt(data_directory + file, delimiter=";")
    np.save(output_directory + id_, array)
    print("File {} processed...".format(id_))