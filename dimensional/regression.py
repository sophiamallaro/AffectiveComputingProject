import pickle
import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.svm import LinearSVR, SVR
from sklearn.linear_model import LinearRegression, LogisticRegression

def train_test(train_df, train_target, test_df, test_target, label, regressor, save = False, **kwargs):
    train_target = (train_target - 1)/8
    test_target = (test_target - 1)/8
    model = regressor(**kwargs)
    model.fit(train_df, train_target[label])
    predictions = model.predict(test_df)
    mae = mean_absolute_error(test_target[label].values, predictions)
    r2 = r2_score(test_target[label].values, predictions)
    print("{} mae = {:.3f}".format(label, mae))
    print("{} r2 = {:.3f}".format(label, r2))
    if save:
        pickle.dump(model, open("{}_model.pkl".format(label), "wb"))
        print("{} model saved to {}_model.pkl".format(label, label))
    print()

def load_model_test(df, target, label):
    target = (target - 1)/8
    model = pickle.load(open("{}_model.pkl".format(label), "rb"))
    print("{} model loaded".format(label))
    predictions = model.predict(df)
    true = target[label].values
    mae = mean_absolute_error(true, predictions)
    r2 = r2_score(true, predictions)
    print("{} mae = {:.3f}".format(label, mae))
    print("{} r2 = {:.3f}".format(label, r2))
    print()

def main():
    df_2013 = pd.read_csv("aggregate/aggregate_2013.csv", index_col = 0, header = 0)
    df_2014 = pd.read_csv("aggregate/aggregate_2014.csv", index_col = 0, header = 0)
    target_2013 = pd.read_csv("annotations/annotations_2013.csv", index_col = 0, header = 0)
    target_2014 = pd.read_csv("annotations/annotations_2014.csv", index_col = 0, header = 0)

    train_test(df_2014, target_2014, df_2013, target_2013, "arousal", SVR, save = True, gamma = "scale")
    train_test(df_2014, target_2014, df_2013, target_2013, "valence", SVR, save = True, gamma = "scale")

    load_model_test(df_2013, target_2013, "arousal")
    load_model_test(df_2013, target_2013, "valence")

if __name__ == "__main__":
    main()