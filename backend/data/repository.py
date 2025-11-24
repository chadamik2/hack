import pandas as pd
from typing import Literal

from sqlalchemy.engine import Engine
from sqlalchemy import inspect

from core.config import engine, get_db


class DataRepository:
    def __init__(self):
        self.db = get_db()

    @staticmethod
    def _append_dataframe(
        df: pd.DataFrame,
        table_name: Literal["supplies", "weather", "temperature", "fires"],
        engine_: Engine,
    ) -> int:
        if df.empty:
            return 0

        df = df.drop_duplicates()

        inspector = inspect(engine_)
        table_names = inspector.get_table_names()

        if table_name not in table_names:
            df.to_sql(table_name, engine_, if_exists="append", index=False)
            return len(df)

        try:
            existing = pd.read_sql_table(table_name, engine_)
        except Exception:
            df.to_sql(table_name, engine_, if_exists="append", index=False)
            return len(df)

        if existing.empty:
            df.to_sql(table_name, engine_, if_exists="append", index=False)
            return len(df)

        common_cols = [col for col in df.columns if col in existing.columns]

        if not common_cols:
            df.to_sql(table_name, engine_, if_exists="append", index=False)
            return len(df)

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
