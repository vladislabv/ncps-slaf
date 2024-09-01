""" if gread_search == False, make sure that first values in the lists are depicting model you want to train"""
class Config:
    PATH = "data/csv/AEP_hourly_cleaned.csv"#"data/parquet/est_hourly.parquet"
    STATION = "AEP_MW"
    FEATURES_LIST = [
        # "Mo",
        # "Di",
        # "Mi",
        # "Do",
        # "Fr",
        # "Sa",
        # "Holiday",
        "WorkDay",
        # "LastDayWasNotWorkDay",
        # "LastDayWasNotWorkDayAndNowWorkDay",
        # "NextDayIsNotWorkDayAndNowWorkDay",
        "LastDayWasHolodiayAndNotWeekend",
        "NextDayIsHolidayAndNotWeekend",
        "MeanLastWeek",
        "MeanLastTwoDays",
        "MaxLastOneDay",
        "MinLastOneDay"
    ]
    FEATURES_2_SCALE = [
        "value",
        "MeanLastWeek",
        "MeanLastTwoDays",
        "MaxLastOneDay",
        "MinLastOneDay"
    ]

    YEAR_SHIFT = 365
    WEEK_SHIFT = 7
    VALUES_PER_DAY = 24
    FILTER_DT_FROM = "2014-01-01 00:00:00"
    FILTER_DT_TILL = "2017-01-01 00:00:00"
    
    GRID_SEARCH = True

    BATCH_SIZE = 7*24
    NUM_WORKERS = 8
    NUM_LNN_UNITS = [16, 8, 32]

    USE_SWISH_ACTIVATION = [False, True]
    INIT_LR = [0.01, 0.0001]
    NUM_EPOCHS = [10, 50, 100]