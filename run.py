import os
import itertools
from datetime import datetime

import pandas as pd

import torch
import torch.utils.data as data_utils
import pytorch_lightning as pl

from ncps.wirings import AutoNCP
from ncps.torch import LTC
from sklearn.preprocessing import MinMaxScaler

import project.utils as utils
from config import Config
from project.model import SequenceLearner


def read_data(path) -> pd.Series:
    _, ext = os.path.splitext(path)
    if ext == ".parquet":
        df = pd.read_parquet(path)
    elif ext == '.csv':
        df = pd.read_csv(path, low_memory=False)
    else:
        raise ValueError("File extension is not supported")
    return df


def grid_search(dataloader, device, in_features, out_features):
    best_train_loss = float('inf')
    best_model_path = None

    # Generate all combinations of hyperparameters
    for lnn_units, lr, num_epochs, lnn_modified in itertools.product(
        Config.NUM_LNN_UNITS,
        Config.INIT_LR,
        Config.NUM_EPOCHS,
        Config.USE_SWISH_ACTIVATION
    ):
        wiring = AutoNCP(lnn_units, out_features)

        ltc_model = LTC(
            in_features,
            wiring,
            batch_first=True,
            use_swish_activation=lnn_modified
        )
        ltc_model.to(device)

        learn = SequenceLearner(
            ltc_model,
            lr=lr,
            features_num=in_features,
            device=device
        )

        # Checkpoint callback to save the best model for this set of hyperparameters
        checkpoint_callback = pl.callbacks.ModelCheckpoint(
            monitor='train_loss',
            dirpath=Config.CHECKPOINTS_PATH,
            filename=f'model-lnn_units={lnn_units}-lr={lr}-num_epochs={num_epochs}-lnn_modified={lnn_modified}_{str(datetime.now()).replace(":","-")}',
            save_top_k=1,
            mode='min'
        )

        # Trainer
        trainer = pl.Trainer(
            max_epochs=num_epochs,
            callbacks=[checkpoint_callback],
            logger=pl.loggers.CSVLogger("log"),
            gradient_clip_val=1,  # Clip gradient to stabilize training
            # manual uncomment if using gpu for training
            # gpus=1 if device == "cuda" else 0
        )

        # Train the model
        trainer.fit(learn, dataloader)

        # Check if this model is the best
        if checkpoint_callback.best_model_score < best_train_loss:
            best_train_loss = checkpoint_callback.best_model_score
            best_model_path = checkpoint_callback.best_model_path

    print(f'Best model saved at: {best_model_path} with validation loss: {best_train_loss}')

    return best_model_path


def train(device="cpu"):
    
    best_model_path = None

    data_raw = read_data(Config.PATH)
    data_raw = utils.prepare_data(data_raw, station=Config.STATION, features=Config.FEATURES_LIST)

    train_data = data_raw.copy()
    
    train_data = utils.make_features(train_data, features=Config.FEATURES_LIST)
    
    x_features, y_features = utils.generate_train_data(
        train_data, features=Config.FEATURES_LIST,
        dt_from=Config.FILTER_DT_FROM, dt_till=Config.FILTER_DT_TILL
    )

    if Config.SCALE_OPTION == 'global':
        min_value, max_value = data_raw.value.min(), data_raw.value.max()
        x_features = (x_features - min_value) / (max_value - min_value)
        y_features = (y_features - min_value) / (max_value - min_value)
    
    if Config.SCALE_OPTION == 'local':
        x_train_scaler = MinMaxScaler()
        y_train_scaler = MinMaxScaler()
        
        x_train_scaler, x_features = utils.normalize_data(
            x_train_scaler,
            x_features)

        y_train_scaler, y_features = utils.normalize_data(
            y_train_scaler,
            y_features)

    out_features = y_features.shape[-1]
    in_features = x_features.shape[-1]

    ds = data_utils.TensorDataset(
        torch.Tensor(x_features), torch.Tensor(y_features)
    )

    dataloader = data_utils.DataLoader(
        ds,
        batch_size=Config.BATCH_SIZE,
        num_workers=Config.NUM_WORKERS,
        shuffle=False,
        persistent_workers=True,
    )
    
    if Config.GRID_SEARCH:
        best_model_path = grid_search(
            dataloader=dataloader,
            device=device,
            in_features=in_features,
            out_features=out_features
        )

        return best_model_path

    wiring = AutoNCP(Config.NUM_LNN_UNITS[0], out_features)  # 16 units, 1 motor neuron

    ltc_model = LTC(
        in_features,
        wiring,
        batch_first=True,
        use_swish_activation=Config.USE_SWISH_ACTIVATION[0]
    )
    ltc_model.to(device)

    learn = SequenceLearner(ltc_model, lr=Config.INIT_LR[0], features_num=in_features, device=device)

    checkpoint_callback = pl.callbacks.ModelCheckpoint(
        dirpath=Config.CHECKPOINTS_PATH,
        filename=f'model-lnn_units={Config.NUM_LNN_UNITS[0]}-lr={Config.INIT_LR[0]}-num_epochs={Config.NUM_EPOCHS[0]}-lnn_modified={Config.USE_SWISH_ACTIVATION[0]}_{str(datetime.now()).replace(":","-")}',
        save_top_k=1,
        monitor="train_loss",
        mode="min"
    )

    trainer = pl.Trainer(
        callbacks=[checkpoint_callback],
        logger=pl.loggers.CSVLogger("log"),
        max_epochs=Config.NUM_EPOCHS[0],
        gradient_clip_val=1,  # Clip gradient to stabilize training
        # manual uncomment if using gpu for training
        # gpus=1 if device == "cuda" else 0
    )

    # Train the model
    trainer.fit(learn, dataloader)
    best_model_path = checkpoint_callback.best_model_path
    best_train_loss = checkpoint_callback.best_model_score

    print(f'Best model saved at: {best_model_path} with validation loss: {best_train_loss}')

    return best_model_path


def evaluate(model_path=None):
    # TBD
    pass


def main():
    model_path = None
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if Config.TRAIN:
        model_path = train(device)

    if Config.EVALUATE:
        evaluate(model_path)


if __name__ == '__main__':
    main()
