# data/repository.py
from typing import Literal

import pandas as pd
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from core.config import get_db

from core.config import engine


class DataRepository:
    def __init__(self):
        self.db = get_db()  # пока не используем, но пригодится для других функций

    @staticmethod
    def _append_dataframe(
        df: pd.DataFrame,
        table_name: Literal["supplies", "weather", "temperature"],
        engine_: Engine,
    ) -> int:
        """
        Добавляет строки из df в таблицу table_name.
        Возвращает количество добавленных строк.
        """
        if df.empty:
            return 0

        # при желании можешь тут сделать очистку/приведение типов/удаление дублей
        df.to_sql(table_name, engine_, if_exists="append", index=False)
        return len(df)

    def upload_supplies(self, df: pd.DataFrame) -> int:
        return self._append_dataframe(df, "supplies", engine)

    def upload_weather(self, df: pd.DataFrame) -> int:
        return self._append_dataframe(df, "weather", engine)

    def upload_temperature(self, df: pd.DataFrame) -> int:
        return self._append_dataframe(df, "temperature", engine)

    def upload_fires(self, df: pd.DataFrame) -> int:
        return self._append_dataframe(df, "fires", engine)

repo = DataRepository()