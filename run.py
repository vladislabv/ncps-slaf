import os
import itertools

import numpy as np
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
        df = pd.read_csv(path)
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
        wiring = AutoNCP(lnn_units, out_features)  # 16 units, 1 motor neuron

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
            dirpath='/home/vlsta001/git_projects/ncps-slaf/slaf-project/checkpoints',
            filename=f'model-lnn_units={lnn_units}-lr={lr}-num_epochs={num_epochs}-lnn_modified={lnn_modified}',
            save_top_k=1,
            mode='min'
        )

        # Trainer
        trainer = pl.Trainer(
            max_epochs=num_epochs,
            callbacks=[checkpoint_callback],
            logger=pl.loggers.CSVLogger("log"),
            gradient_clip_val=1,  # Clip gradient to stabilize training
            gpus=1 if device == "cuda" else 0
        )

        # Train the model
        trainer.fit(learn, dataloader)

        # Check if this model is the best
        if checkpoint_callback.best_model_score < best_train_loss:
            best_train_loss = checkpoint_callback.best_model_score
            best_model_path = checkpoint_callback.best_model_path

    print(f'Best model saved at: {best_model_path} with validation loss: {best_train_loss}')



def main():
    device = "cpu" #"cuda" if torch.cuda.is_available() else "cpu"
    # data related section
    data_raw = read_data(Config.PATH)
    data_raw = utils.prepare_data(data_raw, station=Config.STATION, features=Config.FEATURES_LIST)

    train_data = data_raw.copy()
    train_scaler = MinMaxScaler()
    train_scaler, train_data[Config.FEATURES_2_SCALE] = utils.normalize_data(
        train_scaler,
        train_data[Config.FEATURES_2_SCALE].values)

    train_data = utils.make_features(train_data, features=Config.FEATURES_LIST)

    x_features, y_features = utils.generate_train_data(
        train_data, features=Config.FEATURES_LIST,
        dt_from=Config.FILTER_DT_FROM, dt_till=Config.FILTER_DT_TILL
    )

    ds = data_utils.TensorDataset(
        x_features, y_features
    )

    dataloader = data_utils.DataLoader(
        ds,
        batch_size=Config.BATCH_SIZE * Config.VALUES_PER_DAY,
        num_workers=Config.NUM_WORKERS,
        shuffle=True, 
    )

    out_features = y_features.shape[-1]
    in_features = x_features.shape[-1]
    
    if not Config.GRID_SEARCH:

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
            dirpath="pl_checkpoints",
            save_top_k=5,
            monitor="train_loss"
        )

        trainer = pl.Trainer(
            callbacks=[checkpoint_callback],
            logger=pl.loggers.CSVLogger("log"),
            max_epochs=Config.NUM_EPOCHS[0],
            gradient_clip_val=1,  # Clip gradient to stabilize training
            accelerator='gpu',
            devices=2
            #gpus=2 if device == "cuda" else 0
        )

        # Train the model
        trainer.fit(learn, dataloader)
        print(checkpoint_callback.best_model_path)
    else:
        grid_search(
            dataloader=dataloader,
            device=device,
            in_features=in_features,
            out_features=out_features
        )

#     test_data = data_raw.copy()
#     test_data.value, min_value, max_value = utils.normalize_data(
#         test_data.value)
    
#     test_data = utils.make_features(test_data, features=Config.FEATURES_LIST)
    
#     x_features, y_features = utils.generate_test_data(
#         test_data,
#         Config.FILTER_DT,
#         features=Config.FEATURES_LIST,
#         push_y_by = 7,
#         unit = 'd',
#     )
    
#     ds = data_utils.TensorDataset(
#         x_features, y_features
#     )

#     dataloader = data_utils.DataLoader(
#         ds,
#         batch_size=Config.BATCH_SIZE,
#         num_workers=Config.NUM_WORKERS,
#         shuffle=False, 
#     )
    
#     if not Config.GRID_SEARCH:
#         ltc_model.to(device)
#         with torch.no_grad():
#             prediction = ltc_model(x_features.view(1, -1, in_features).to(device))[0].cpu().numpy()

#         prediction = utils.denormalize_data(prediction, min_value, max_value)

    return # ltc_model, x_features, y_features


if __name__ == '__main__':
    main()