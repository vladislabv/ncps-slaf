from datetime import datetime, timedelta
from typing import Tuple, Union, Dict

from torch import Tensor
from numpy import ndarray, transpose, float64
from pandas import DataFrame, Series

from config import Config


def prepare_data(df: DataFrame, station: str, features: list[str] = []) -> DataFrame:
    """Makes sure that the incoming data
    1. has no duplicated indexes,
    2. has no duplicated values,
    3. has validated column names,
    4. has ascending sorted datetime index.

    Args:
        df (DataFrame): not validated dataframe of raw time-series data.
        station (str): name of station to use for training.
        features (list, optional): list of column names should be taken into training. Defaults to [].

    Returns:
        DataFrame: DataFrame meeting all the requirements.
    """
    df = df.reset_index()[["Datetime", station, *features]].rename(
        columns={
            "Datetime": "datetime",
            station: "value"
        }
    )
    df = df.set_index("datetime")

    sorted_idx = df.index.sort_values()
    
    df = df.loc[sorted_idx]
    df = df.dropna()
    df = df[~df.index.duplicated(keep='first')]

    return df


def normalize_data(scaler, data: Union[ndarray, Tensor]) -> Dict:
    return scaler, scaler.fit_transform(data)


def denormalize_data(scaler, data: Union[ndarray, Tensor]) -> Union[ndarray, Tensor]:
    return scaler.inverse_transform(data)


def make_features(df: Series, features: list[str] = []) -> DataFrame:
    """Here take following actions in-place
    1. converts all existing features to uninfied format, e.g. float64,
    2. adds shifted variables (year, week) shift to the df.

    Args:
        df (Series): dataframe of time-series data.
        features (list, optional): list of column names should be taken into training. Defaults to [].

    Returns:
        DataFrame: dataframe containing all features for training.
    """
    values = df.value.values
    # convert features to unified format // float64
    features_values = []
    if features:
        features_values = transpose(df[features].values)
        features_values = features_values.astype(float64)
    
    # x = y(-1d)
    x = values[(Config.YEAR_SHIFT * Config.VALUES_PER_DAY) - Config.VALUES_PER_DAY:]
    # x_week = y(-7d)
    x_shifted_week = values[(Config.YEAR_SHIFT - Config.WEEK_SHIFT) * Config.VALUES_PER_DAY:]
    # x_year = y(-365d)
    x_shifted_year = values
    # y = y(0d)
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
        df: DataFrame, features: list[str] = [], dt_from: str = "", dt_till: str = None) -> Tuple[ndarray]:
    """Generates training dataset based on acquired arguments.

    Args:
        df (DataFrame): dataframe containing all features for training.
        features (list, optional): list of column names should be taken into training dataset. Defaults to [].
        dt_from (str, optional): point of time where the dataset should start. Defaults to "".
        dt_till (str, optional): point of time where the dataset should end. Defaults to "".

    Returns:
        Tuple[ndarray]: X and Y as numpy arrays.
    """
    if dt_from:
        df = df[df.index > dt_from]
    if dt_till:
        df = df[df.index < dt_till]

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
        last_seen_dt: str,
        features: list[str] = [],
        push_y_by = 7,
        unit = 'd'
    ) -> Tuple[ndarray]:
    """Generates test dataset based on acquired arguments.
    Calls internally `generate_train_data()`.

    Args:
        df (DataFrame): dataframe containing all features for predictions making.
        last_seen_dt (str): the latest point of time was used in the training dataset. 
        features (list[str], optional): list of column names should be taken into training dataset. Defaults to [].
        push_y_by (int, optional): Number of units the boundaries of training data should be pushed by. Defaults to 7.
        unit (str, optional): Name of unit, e.g. d for days, w for weeks and so on. Defaults to 'd'.

    Returns:
        Tuple[ndarray]: X and Y as numpy arrays.
    """
    # push datetime by given units into future
    dt_till = datetime.fromisoformat(last_seen_dt) \
        + timedelta(days=push_y_by)
    
    dt_till = dt_till.isoformat().replace('T', ' ')

    return generate_train_data(df, features=features, dt_from=last_seen_dt, dt_till=dt_till)
