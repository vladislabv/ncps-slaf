"""Configuration used for training as well as evaluating the model.

FILTER_DT_FROM, FILTER_DT_TILL (in the ISO-format "%Y-%m-%d %H:%M:%S")
used to create your train data.

By default GRID_SEARCH is disabled. When it is disabled, the hyperparameters for training
will be values stored at the index 0. Else all values will be used to form models from parameter combinations.
"""
class Config:

    # dataset specific variables
    PATH: str = "data/csv/AEP_hourly_cleaned.csv"
    STATION: str = "AEP_MW"
    FEATURES_LIST: list = [
        "WorkDay",
        "LastDayWasHolodiayAndNotWeekend",
        "NextDayIsHolidayAndNotWeekend",
        "MeanLastWeek",
        "MeanLastTwoDays",
        "MaxLastOneDay",
        "MinLastOneDay"
    ]
    FEATURES_2_SCALE: list = [
        "value",
        "MeanLastWeek",
        "MeanLastTwoDays",
        "MaxLastOneDay",
        "MinLastOneDay"
    ]

    YEAR_SHIFT: int = 365
    WEEK_SHIFT: int = 7
    VALUES_PER_DAY: int = 24
    FILTER_DT_FROM: str = "2014-01-01 00:00:00"
    FILTER_DT_TILL: str = "2017-01-01 00:00:00"


    # global settings
    TRAIN: bool = True
    EVALUATE: bool = False
    GRID_SEARCH: bool = False
    CHECKPOINTS_PATH = "pl_checkpoints/"


    # torch Dataloader related
    BATCH_SIZE: int = 7 * 24
    NUM_WORKERS: int = 1


    # hyperparameters of LNN
    NUM_LNN_UNITS: list = [16, 8, 32]
    USE_SWISH_ACTIVATION: list = [False, True]
    INIT_LR: list = [0.01, 0.0001]
    NUM_EPOCHS: list = [10, 50, 100]