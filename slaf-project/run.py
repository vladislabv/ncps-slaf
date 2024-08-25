import numpy as np
import pandas as pd

import torch
import torch.utils.data as data_utils
import pytorch_lightning as pl

from ncps.wirings import AutoNCP
from ncps.torch import LTC

import src.utils as utils
from config import Config
from src.model import SequenceLearner


def read_data(path) -> pd.Series:
    df = pd.read_parquet(path)
    return df


def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # data related section
    data_raw = read_data(Config.PATH)
    data_raw = utils.prepare_data(data_raw, station=Config.STATION)

    train_data = data_raw.copy()
    train_data.value, min_value, max_value = utils.normalize_data(
        train_data.value)

    train_data = utils.make_features(train_data)

    x_features, y_features = utils.generate_train_data(
        train_data, dt_till=Config.FILTER_DT
    )

    ds = data_utils.TensorDataset(
        x_features, y_features
    )

    dataloader = data_utils.DataLoader(
        ds,
        batch_size=Config.BATCH_SIZE,
        num_workers=Config.NUM_WORKERS,
        shuffle=True, 
    )

    out_features = y_features.shape[-1]
    in_features = x_features.shape[-1]

    wiring = AutoNCP(Config.NUM_LNN_UNITS, out_features)  # 16 units, 1 motor neuron

    ltc_model = LTC(
        in_features,
        wiring,
        batch_first=True,
        use_swish_activation=Config.USE_SWISH_ACTIVATION
    )

    learn = SequenceLearner(ltc_model, lr=Config.INIT_LR)

    trainer = pl.Trainer(
        logger=pl.loggers.CSVLogger("log"),
        max_epochs=Config.NUM_EPOCHS,
        gradient_clip_val=1,  # Clip gradient to stabilize training
        # gpus=1 if device == "cuda" else 0
    )

    # Train the model
    trainer.fit(learn, dataloader)

    test_data = data_raw.copy()
    test_data.value, min_value, max_value = utils.normalize_data(
        test_data.value)
    
    test_data = utils.make_features(test_data)
    
    x_features, y_features = utils.generate_test_data(
        test_data,
        Config.FILTER_DT,
        push_y_by = 7,
        unit = 'd',
    )

    with torch.no_grad():
        prediction = ltc_model(x_features.view(1, -1, in_features).to(device))[0].cpu().numpy()
    
    prediction = utils.denormalize_data(prediction, min_value, max_value)

    print(prediction)

    return


if __name__ == '__main__':
    main()