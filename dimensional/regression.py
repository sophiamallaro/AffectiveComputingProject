import pickle
import numpy as np
import pandas as pd
from sklearn.svm import LinearSVR, SVR
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.linear_model import LinearRegression, ElasticNet
from sklearn.model_selection import KFold, RepeatedKFold, cross_val_predict

def train_test(train_df, train_target, test_df, test_target, label, regressor, **kwargs):
    model = regressor(**kwargs)
    model.fit(train_df, train_target[label])

    predictions = model.predict(test_df)
    predictions = (predictions - 1)/8
    true = (test_target[label].values - 1)/8

    mae = mean_absolute_error(true, predictions)
    r2 = r2_score(true, predictions)

    print("label = {}".format(label))
    print("{} mae = {:.3f}".format(label, mae))
    print("{} r2 = {:.3f}".format(label, r2))
    print()

def cross_validation(df, target, label, regressor, **kwargs):
    model = regressor(**kwargs)
    predictions = cross_val_predict(model, df, target[label], cv = KFold(10), verbose = 1, n_jobs = -1)
    
    true = target[label].values
    predictions = (predictions - 1)/8
    true = (true - 1)/8
    
    mae = mean_absolute_error(true, predictions)
    r2 = r2_score(true, predictions)

    print("label = {}".format(label))
    print("{} mae = {:.3f}".format(label, mae))
    print("{} r2 = {:.3f}".format(label, r2))
    print()

def train_and_save(df, target, label, estimator, **kwargs):
    model = estimator(**kwargs)
    model.fit(df, target[label])
    
    true = (target[label].values - 1)/8
    predictions = (model.predict(df) - 1)/8

    mae = mean_absolute_error(true, predictions)
    r2 = r2_score(true, predictions)

    print(label)
    print("training mae = {:.3f}".format(mae))
    print("training r2 = {:.3f}".format(r2))
    
    pickle.dump(model, open("{}_model.pkl".format(label), "wb"))
    print("{} model saved to {}_model.pkl".format(label, label))
    print()

def save_means_stds(df):
    scaling = pd.DataFrame(index = df.columns, columns = ["mean","std","min","max"])
    scaling["mean"] = df.mean()
    scaling["std"] = df.std()
    scaling["min"] = df.min()
    scaling["max"] = df.max()
    scaling.to_csv("scaling.csv")
    print("mean, std, min and max calculated and saved")
    print()

def main():
    print()

    df_2013 = pd.read_csv("./aggregate/aggregate_2013.csv", index_col = 0, header = 0)
    df_2014 = pd.read_csv("./aggregate/aggregate_2014.csv", index_col = 0, header = 0)
    target_2013 = pd.read_csv("./annotations/annotations_2013.csv", index_col = 0, header = 0)
    target_2014 = pd.read_csv("./annotations/annotations_2014.csv", index_col = 0, header = 0)

    df = pd.concat([df_2013, df_2014])
    target = pd.concat([target_2013, target_2014])
    df_scaled = pd.DataFrame(index = df.index, columns = df.columns, data = StandardScaler().fit_transform(df.values))
    cross_validation(df_scaled, target, "arousal", SVR, gamma = "scale", C = 1)
    cross_validation(df_scaled, target, "valence", SVR, gamma = "scale", C = 1)

    train_and_save(df_scaled, target, "arousal", SVR, gamma = "scale", C = 1.0)
    train_and_save(df_scaled, target, "valence", SVR, gamma = "scale", C = 1.0)

    save_means_stds(df)

if __name__ == "__main__":
    main()