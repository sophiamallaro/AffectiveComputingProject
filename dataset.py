import torch
from torch.utils import data
import numpy as np
import pandas as pd
class Dataset(data.Dataset):
  'Characterizes a dataset for PyTorch'
  def __init__(self, list_IDs, labels):
        'Initialization'
        self.labels = labels
        self.list_IDs = list_IDs

  def __len__(self):
        'Denotes the total number of samples'
        return len(self.list_IDs)

  def __getitem__(self, index):
        'Generates one sample of data'
        # Select sample
        ID = self.list_IDs[index]

        # Load data and get label
        #X = np.load('data/' + ID + '.npy')
        X = pd.read_csv('pyspec_data/' + ID + '.csv',header=None).values
        X = np.expand_dims(X, axis=0)
        y = self.labels[ID]

        return X, y