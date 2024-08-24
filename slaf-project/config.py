class Config:
    PATH = "data/parquet/est_hourly.parquet"
    STATION = "AEP"

    YEAR_SHIFT = 365
    WEEK_SHIFT = 7
    VALUES_PER_DAY = 24
    FILTER_DT = "2006-01-01 00:00:00"

    BATCH_SIZE = 7
    NUM_WORKERS = 1
    NUM_LNN_UNITS = 16

    USE_SWISH_ACTIVATION = False
    INIT_LR = 0.01
    NUM_EPOCHS = 1