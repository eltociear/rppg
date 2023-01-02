import os
import h5py
import numpy as np
from torch.utils.data import DataLoader

from vid2bp.LSTMAutoEncoder.dataset.LSTMAutoEncoderDataset import LSTMAutoEncoderDataset


def dataset_loader(dataset_name: str = 'mimiciii', channel: int = 1, batch_size: int = 8, label: str = 'ple'):
    train_shuffle: bool = True
    test_shuffle: bool = False

    dataset_root_path: str = '/home/najy/PycharmProjects/vid2bp_datasets/'
    train_file_path = dataset_root_path + "train.hdf5"
    valid_file_path = dataset_root_path + "val.hdf5"
    test_file_path = dataset_root_path + "test.hdf5"
    if os.path.isfile(train_file_path) and os.path.isfile(valid_file_path) and os.path.isfile(test_file_path):
        print("dataset exist")
    else:
        print("preprocessing needed")

    with h5py.File(train_file_path, 'r') as train_data:
        train_ple = np.array(train_data['ple'][:, 0])
        train_abp = np.array(train_data['abp'])

    with h5py.File(valid_file_path, 'r') as valid_data:
        valid_ple = np.array(valid_data['ple'][:, 0])
        valid_abp = np.array(valid_data['abp'])

    with h5py.File(test_file_path, 'r') as test_data:
        test_ple = np.array(test_data['ple'][:, 0])
        test_abp = np.array(test_data['abp'])

    if label == 'ple':
        train_dataset = LSTMAutoEncoderDataset(train_ple, train_ple)
        valid_dataset = LSTMAutoEncoderDataset(valid_ple, valid_ple)
        test_dataset = LSTMAutoEncoderDataset(test_ple, test_ple)
    elif label == 'abp':
        train_dataset = LSTMAutoEncoderDataset(train_ple, train_abp)
        valid_dataset = LSTMAutoEncoderDataset(valid_ple, valid_abp)
        test_dataset = LSTMAutoEncoderDataset(test_ple, test_abp)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=train_shuffle)
    valid_loader = DataLoader(valid_dataset, batch_size=batch_size, shuffle=test_shuffle)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=test_shuffle)

    return [train_loader, valid_loader, test_loader]
