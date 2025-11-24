# data/repository.py
from typing import Literal

import pandas as pd
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from core.config import get_db

from core.config import engine


import pandas as pd
from typing import Literal

from sqlalchemy.engine import Engine
from sqlalchemy import inspect

from core.config import engine, get_db


class DataRepository:
    def __init__(self):
        # если потребуется сессия: self.db = next(get_db())
        self.db = get_db()

    @staticmethod
    def _append_dataframe(
        df: pd.DataFrame,
        table_name: Literal["supplies", "weather", "temperature", "fires"],
        engine_: Engine,
    ) -> int:
        """
        Добавляет в таблицу только новые строки (без дубликатов).
        Дубликат = строка, у которой значения всех общих колонок
        совпадают с уже существующей строкой в таблице.
        Возвращает количество добавленных строк.
        """
        if df.empty:
            return 0

        # убираем дубли внутри самого файла
        df = df.drop_duplicates()

        inspector = inspect(engine_)
        table_names = inspector.get_table_names()

        # если таблицы ещё нет – просто создаём её из df
        if table_name not in table_names:
            df.to_sql(table_name, engine_, if_exists="append", index=False)
            return len(df)

        # таблица есть – читаем существующие данные
        try:
            existing = pd.read_sql_table(table_name, engine_)
        except Exception:
            # если по какой-то причине не удалось прочитать – на всякий
            df.to_sql(table_name, engine_, if_exists="append", index=False)
            return len(df)

        if existing.empty:
            # в таблице нет строк – можно просто вставить df
            df.to_sql(table_name, engine_, if_exists="append", index=False)
            return len(df)

        # общие колонки между df и таблицей
        common_cols = [col for col in df.columns if col in existing.columns]

        if not common_cols:
            # если общих колонок нет, нечем сравнивать – считаем всё новым
            df.to_sql(table_name, engine_, if_exists="append", index=False)
            return len(df)

        # оставляем только строки, которых ещё нет в таблице
        existing_keys = existing[common_cols].drop_duplicates()

        merged = df.merge(
            existing_keys,
            on=common_cols,
            how="left",
            indicator=True,
        )

        df_new = merged[merged["_merge"] == "left_only"].drop(columns=["_merge"])

        if df_new.empty:
            return 0

        df_new.to_sql(table_name, engine_, if_exists="append", index=False)
        return len(df_new)

    def upload_supplies(self, df: pd.DataFrame) -> int:
        return self._append_dataframe(df, "supplies", engine)

    def upload_weather(self, df: pd.DataFrame) -> int:
        return self._append_dataframe(df, "weather", engine)

    def upload_temperature(self, df: pd.DataFrame) -> int:
        return self._append_dataframe(df, "temperature", engine)

    def upload_fires(self, df: pd.DataFrame) -> int:
        return self._append_dataframe(df, "fires", engine)


repo = DataRepository()