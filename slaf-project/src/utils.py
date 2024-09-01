from datetime import datetime, timedelta
from typing import Tuple, Union, Dict

from torch import Tensor
from numpy import ndarray, array, transpose, float64
from pandas import DataFrame, Series

from config import Config


def prepare_data(df: DataFrame, station: str, features: list = []) -> Series:
    df = df.reset_index()[["Datetime", station, *features]].rename(
        columns={
            "Datetime": "datetime",
            station: "value"
        }
    )
    df = df.set_index("datetime")
    # make sure idx is filterd ascending way
    sorted_idx = df.index.sort_values()
    df = df.loc[sorted_idx]
    df = df.dropna()
    df = df[~df.index.duplicated(keep='first')]

    return df


def normalize_data(scaler, data: Union[ndarray, Tensor]) -> Dict:
    # Min-Max Normalization
    return scaler, scaler.fit_transform(data)


def denormalize_data(
        scaler,
        data: Union[ndarray, Tensor],
    ) -> Union[ndarray, Tensor]:
    return scaler.inverse_transform(data)


def make_features(df: Series, features: list = []) -> DataFrame:
    values = df.value.values
    features_values = []
    if features:
        features_values = transpose(df[features].values)
        features_values = features_values.astype(float64)
    
    # y(-1)
    x = values[(Config.YEAR_SHIFT * Config.VALUES_PER_DAY) - Config.VALUES_PER_DAY:]
    # y(-7)
    x_shifted_week = values[(Config.YEAR_SHIFT - Config.WEEK_SHIFT) * Config.VALUES_PER_DAY:]
    # y(-365)
    x_shifted_year = values
    # y(0)
    y = values[(Config.YEAR_SHIFT * Config.VALUES_PER_DAY):]

    rcut_idx = min(
        len(x),
        len(y),
        len(x_shifted_week),
        len(x_shifted_year),
    )

    idx = df.index.copy()
    idx = idx[
        (Config.YEAR_SHIFT * Config.VALUES_PER_DAY): \
            rcut_idx + (Config.YEAR_SHIFT * Config.VALUES_PER_DAY)
    ]
    del df
    data = {
        **{
            "x": x[:rcut_idx],
            "y": y[:rcut_idx],
            "x_shifted_week": x_shifted_week[:rcut_idx],
            "x_shifted_year": x_shifted_year[:rcut_idx],
        },
        **{k: v[:rcut_idx] for k, v in zip(features, features_values)}
    }
    df = DataFrame(data)
    df.index = idx
    
    del x, y, x_shifted_week, x_shifted_year, idx, features_values, data

    return df


def generate_train_data(
        df: DataFrame, features: list = [], dt_from = None, dt_till = None) -> Tuple[Tensor]:
    if dt_from:
        df = df[df.index > dt_from]
    if dt_till:
        df = df[df.index < dt_till]
<<<<<<< HEAD
=======
        
    # print(df)
>>>>>>> 2493d79fa1c884ba2dde418752c106b7f6d8fffd

    y = df.y.values.reshape(-1, 1)
    x = df[[
            "x",
            "x_shifted_week",
            "x_shifted_year",
            *features
        ]].values

    return x, y


def generate_test_data(
        df: DataFrame,
        last_seen_dt: datetime,
        features: list = [],
        push_y_by = 7,
        unit = 'days'
    ) -> Tuple[Tensor]:
    # push datetime by given units into future
    dt_till = datetime.fromisoformat(last_seen_dt) \
        + timedelta(days=push_y_by)
    
    dt_till = dt_till.isoformat().replace('T', ' ')

    return generate_train_data(df, features=features, dt_from=last_seen_dt, dt_till=dt_till)
