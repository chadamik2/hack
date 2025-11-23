# пример использования
from datetime import date

import pandas as pd

from core.config import engine  # тот же engine, что и в API
from ml.model import FireModel


def run_fire_prediction_for_date(target_date: date) -> pd.DataFrame:
    # читаем таблицы из той же БД, куда раньше грузили CSV
    supplies = pd.read_sql("SELECT * FROM supplies", engine, parse_dates=["date"])
    temperature = pd.read_sql(
        "SELECT * FROM temperature", engine, parse_dates=["date"]
    )
    weather = pd.read_sql("SELECT * FROM weather", engine, parse_dates=["date"])

    model = FireModel()
    return model.predict(target_date, supplies, temperature, weather)


# пример вызова:
# df_pred = run_fire_prediction_for_date(date(2021, 5, 1))
