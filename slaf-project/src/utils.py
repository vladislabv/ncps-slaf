from datetime import datetime, timedelta
from typing import Tuple, Union, Dict

from torch import Tensor
from numpy import ndarray, array, transpose
from pandas import DataFrame, Series

from config import Config


def prepare_data(df: DataFrame, station: str) -> Series:
    df = df.reset_index()[["Datetime", station]].rename(
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


def normalize_data(data: Union[ndarray, Tensor]) -> Dict:
    # Min-Max Normalization
    mmin = data.min()
    mmax = data.max()

    return (
        (data - mmin) / (mmax - mmin),
        mmin,
        mmax,
    )


def denormalize_data(
        data: Union[ndarray, Tensor],
        min_value: float,
        max_value: float
    ) -> Union[ndarray, Tensor]:
    return data * (max_value - min_value) + min_value


def make_features(df: Series) -> DataFrame:
    values = df.value.values

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
    df = DataFrame(
        {
            "x": x[:rcut_idx],
            "y": y[:rcut_idx],
            "x_shifted_week": x_shifted_week[:rcut_idx],
            "x_shifted_year": x_shifted_year[:rcut_idx],
        }
    )
    df.index = idx
    
    del x, y, x_shifted_week, x_shifted_year, idx

    return df


def generate_train_data(
        df: DataFrame, dt_from = None, dt_till = None) -> Tuple[Tensor]:
    if dt_from:
        df = df[df.index > dt_from]
    if dt_till:
        df = df[df.index < dt_till]

    tensor_y = Tensor(df.y.values).view((-1, 1))
    tensor_x = Tensor(
        transpose(array([
            df.x.values,
            df.x_shifted_week.values,
            df.x_shifted_year.values,
        ]))
    )

    return tensor_x, tensor_y


def generate_test_data(
        df: DataFrame,
        last_seen_dt: datetime,
        push_y_by = 7,
        unit = 'days'
    ) -> Tuple[Tensor]:
    # push datetime by given units into future
    dt_till = datetime.fromisoformat(last_seen_dt) \
        + timedelta(days=push_y_by)
    
    dt_till = dt_till.isoformat().replace('T', ' ')

    return generate_train_data(df, dt_from=last_seen_dt, dt_till=dt_till)
