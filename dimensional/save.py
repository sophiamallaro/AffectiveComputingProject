import os
import pandas as pd

def save_data():
    feature_directory = "./features/"
    file_names = os.listdir(feature_directory)
    columns = list(pd.read_csv(feature_directory + file_names[0], delimiter = ";", index_col = 0, header = 0).columns)
    columns = [column for column in columns if column.endswith("_amean")]
    mean_columns = [column[:-6] + "_mean" for column in columns]
    std_columns = [column[:-6] + "_std" for column in columns]
    song_ids = sorted([int(file_name.split(".")[0]) for file_name in file_names])
    df = pd.DataFrame(index = song_ids, columns = mean_columns + std_columns)
    
    for song_id in song_ids:
        song_df = pd.read_csv(feature_directory + "{}.csv".format(song_id), delimiter = ";", index_col = 0, header = 0)
        df.loc[song_id, mean_columns] = song_df[columns].mean().values
        df.loc[song_id, std_columns] = song_df[columns].std().values
        print("done aggregating {}.csv".format(song_id))
    
    df.to_csv("aggregate.csv")

def save_year_data():
    df = pd.read_csv("aggregate.csv", index_col = 0, header = 0)
    df_2013 = df.loc[df.index <= 1000].copy()
    df_2014 = df.loc[(df.index > 1000) & (df.index <= 2000)].copy()
    df_2015 = df.loc[df.index > 2000].copy()
    df_2013.to_csv("aggregate_2013.csv")
    df_2014.to_csv("aggregate_2014.csv")
    df_2015.to_csv("aggregate_2015.csv")

def save_annotations():
    df = pd.read_csv("annotations/static_annotations_averaged_songs_1_2000.csv", index_col = 0, header = 0)
    df.rename(columns = {" valence_mean":"valence", " arousal_mean":"arousal"}, inplace = True)
    df_2013 = df.loc[df.index <= 1000, ("arousal","valence")].copy()
    df_2014 = df.loc[(df.index > 1000) & (df.index <= 2000), ("arousal","valence")].copy()
    df_2013.to_csv("annotations_2013.csv")
    df_2014.to_csv("annotations_2014.csv")

    df = pd.read_csv("annotations/static_annotations_averaged_songs_2000_2058.csv", index_col = 0, header = 0)
    df.rename(columns = {" valence_mean":"valence", " arousal_mean":"arousal"}, inplace = True)
    df_2015 = df[["arousal","valence"]].copy()
    df_2015.to_csv("annotations_2015.csv")

if __name__ == "__main__":
    # save_data()
    # save_year_data()
    save_annotations()