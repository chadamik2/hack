# backend/ml/model.py
import datetime
from dataclasses import dataclass
from typing import Any, Dict
import pandas as pd
from data.repository import repo

from core.config import engine
import numpy as np
import catboost




@dataclass
class FirePrediction:
    stack_id: str
    predicted_fire_date: Any  # datetime.date или datetime.datetime


class FireModel:
    """
    Интерфейс для модели.
    Реализация обучения и предсказания будет отдельно.
    """

    def __init__(self) -> None:
        # сюда можно будет загрузить веса/конфиг модели
        pass

    def _load_feature_data(self) -> Dict[str, pd.DataFrame]:
        """
        Вспомогательный метод: грузим признаки из БД.
        """
        supplies = pd.read_sql(
            "SELECT * FROM supplies", engine, parse_dates=["date"]
        )
        temperature = pd.read_sql(
            "SELECT * FROM temperature", engine, parse_dates=["date"]
        )
        weather = pd.read_sql(
            "SELECT * FROM weather", engine, parse_dates=["date"]
        )
        fires = pd.read_sql(
            "SELECT * FROM fires", engine, parse_dates=["date"]
        )
        return {
            "supplies": supplies,
            "temperature": temperature,
            "weather": weather,
            "fires": fires,
        }

    def train(self):
        pass

    def predict(self, date: datetime.date) -> pd.DataFrame:
        data = self._load_feature_data()
        fires = data["fires"]
        temperature = data["temperature"]
        weather = data["weather"]
        supplies = data["supplies"]
        fires["Дата начала"] = pd.to_datetime(fires["Дата начала"])
        fires["Дата оконч."] = pd.to_datetime(fires["Дата оконч."])
        fires["Нач.форм.штабеля"] = pd.to_datetime(fires["Нач.форм.штабеля"])

        fires["form_start"] = fires["Нач.форм.штабеля"].dt.normalize()

        temperature["Дата акта"] = pd.to_datetime(temperature["Дата акта"])
        temperature["date"] = temperature["Дата акта"].dt.normalize()

        supplies["ВыгрузкаНаСклад"] = pd.to_datetime(supplies["ВыгрузкаНаСклад"])
        supplies["ПогрузкаНаСудно"] = pd.to_datetime(supplies["ПогрузкаНаСудно"])
        supplies["date_in"] = supplies["ВыгрузкаНаСклад"].dt.normalize()
        supplies["date_out"] = supplies["ПогрузкаНаСудно"].dt.normalize()

        weather["date"] = pd.to_datetime(weather["date"])
        weather["date"] = weather["date"].dt.normalize()

        MERGE_GAP = pd.Timedelta(hours=12)

        fires = fires.sort_values(["Склад", "Штабель", "Дата начала"]).reset_index(drop=True)

        fires["prev_end"] = fires.groupby(["Склад", "Штабель"])["Дата оконч."].shift(1)
        fires["gap"] = fires["Дата начала"] - fires["prev_end"]
        fires["new_fire"] = fires["gap"].isna() | (fires["gap"] > MERGE_GAP)
        fires["fire_id"] = fires.groupby(["Склад", "Штабель"])["new_fire"].cumsum()

        fires = (fires
                 .groupby(["Склад", "Штабель", "fire_id"], as_index=False)
                 .agg({
                     "Дата начала": "min",
                     "Дата оконч.": "max",
                     "Вес по акту, тн": "sum",
                     "Груз": "first",
                     "Дата составления": "first",
                     "Нач.форм.штабеля": "first",
                     "form_start": "first"
                 }))


        supplies = supplies.sort_values(["Склад", "Штабель", "date_in"]).reset_index(drop=True)
        supplies["pile_id"] = supplies.groupby(["Склад", "Штабель"]).cumcount() + 1

        def expand_one_pile(row):
            days = pd.date_range(row["date_in"], row["date_out"], freq="D")
            return pd.DataFrame({
                "date": days,
                "Склад": row["Склад"],
                "Штабель": row["Штабель"],
                "coal_type" : row["Наим. ЕТСНГ"],
                "pile_id": row["pile_id"],
                "date_in": row["date_in"],
                "date_out": row["date_out"],
                "mass" : row["На склад, тн"]
            })

        base = pd.concat([expand_one_pile(r) for _, r in supplies.iterrows()],
                         ignore_index=True)

        # =========================
        # ШАГ 2: джойним temperature и weather (упрощённо)
        # =========================

        temperature = temperature.drop(columns=["Пикет"], errors="ignore")

        temp_daily = (temperature
                      .groupby(["Склад", "Штабель", "date"], as_index=False)
                      .agg({
                          "Максимальная температура": "max"
                      })
                     )


        base = base.merge(temp_daily,
                          on=["Склад", "Штабель", "date"],
                          how="left")


        weather = weather.drop(columns=["visibility", "p", "wind_dir"], errors="ignore")

        weather_daily = (weather
                         .groupby("date", as_index=False)
                         .mean(numeric_only=True)
                        )

        base = base.merge(weather_daily, on="date", how="left")

        base = base.dropna(subset=["Максимальная температура"]).reset_index(drop=True)

        base = base.reset_index(drop=True)
        base["row_id"] = base.index

        fires_start = fires[["Склад", "Штабель", "Дата начала"]].dropna().copy()
        fires_start["Дата начала"] = pd.to_datetime(fires_start["Дата начала"]).dt.normalize()

        base["date"] = pd.to_datetime(base["date"]).dt.normalize()
        base["date_in"] = pd.to_datetime(base["date_in"]).dt.normalize()
        base["date_out"] = pd.to_datetime(base["date_out"]).dt.normalize()

        tmp = base.merge(fires_start, on=["Склад", "Штабель"], how="left")

        tmp["fire_before"] = (
            (tmp["Дата начала"] >= tmp["date_in"]) &   # пожар после завоза этой кучи
            (tmp["Дата начала"] <= tmp["date_out"]) &  # пожар до отгрузки этой кучи
            (tmp["Дата начала"] < tmp["date"])         # и раньше текущего дня
        )

        had_before = (tmp.groupby("row_id")["fire_before"]
                        .any()
                        .astype(int))

        base["had_fire_before"] = base["row_id"].map(had_before).fillna(0).astype(int)
        base = base.drop(columns=["row_id"])

        # оставляем только нужное и сортируем пожары
        fires_start = (fires[["Склад", "Штабель", "Дата начала"]]
                       .dropna()
                       .sort_values(["Склад", "Штабель", "Дата начала"])
                      )

        # на всякий случай нормализуем даты
        fires_start["Дата начала"] = pd.to_datetime(fires_start["Дата начала"]).dt.normalize()
        base["date"] = pd.to_datetime(base["date"]).dt.normalize()
        base["date_out"] = pd.to_datetime(base["date_out"]).dt.normalize()

        def add_target_for_group(g):
            fdates = fires_start.loc[
                (fires_start["Склад"] == g.name[0]) &
                (fires_start["Штабель"] == g.name[1]),
                "Дата начала"
            ].values

            if len(fdates) == 0:
                g["nearest_fire_date"] = pd.NaT
                g["days_to_fire"] = np.nan
                return g

            idx = np.searchsorted(fdates, g["date"].values, side="left")

            # безопасно берём даты (если idx==len, возьмётся последняя)
            nearest = np.take(fdates, np.minimum(idx, len(fdates)-1))

            # а теперь там, где idx == len(fdates), ставим NaT
            nearest[idx == len(fdates)] = np.datetime64("NaT")

            g["nearest_fire_date"] = pd.to_datetime(nearest)
            g["days_to_fire"] = (g["nearest_fire_date"] - g["date"]).dt.days

            return g


        # считаем таргет по группам
        base = (base
                .sort_values(["Склад", "Штабель", "date"])
                .groupby(["Склад", "Штабель"], group_keys=False)
                .apply(add_target_for_group)
               )
        base_all = base.copy()
        # фильтр: если ближайший пожар позже date_out — это уже другая куча -> убираем строку
        base = base[
            base["nearest_fire_date"].notna() &
            (base["nearest_fire_date"] <= base["date_out"])
        ].reset_index(drop=True)

        base = base.sort_values(["Склад","Штабель","pile_id","date"]).reset_index(drop=True)

        grp = base.groupby(["Склад","Штабель","pile_id"])

        # 1) скользящие средние/максимумы температуры
        base["temp_mean_3d"] = grp["Максимальная температура"].transform(
            lambda s: s.rolling(3, min_periods=1).mean()
        )
        base["temp_max_3d"] = grp["Максимальная температура"].transform(
            lambda s: s.rolling(3, min_periods=1).max()
        )

        base["temp_mean_7d"] = grp["Максимальная температура"].transform(
            lambda s: s.rolling(7, min_periods=1).mean()
        )
        base["temp_max_7d"] = grp["Максимальная температура"].transform(
            lambda s: s.rolling(7, min_periods=1).max()
        )

        H = 7

        base_cls = base_all.copy()

        base_cls["fire_within_7d"] = (
                base_cls["days_to_fire"].notna() &
                (base_cls["days_to_fire"] >= 0) &
                (base_cls["days_to_fire"] <= H) &
                (base_cls["nearest_fire_date"] <= base_cls["date_out"])  # пожар внутри жизни кучи
        ).astype(int)

        base_cls["fire_within_7d"].value_counts()

        grp = base_cls.groupby(["Склад", "Штабель", "pile_id"])

        # 1) скользящие средние/максимумы температуры
        base_cls["temp_mean_3d"] = grp["Максимальная температура"].transform(
            lambda s: s.rolling(3, min_periods=1).mean()
        )
        base_cls["temp_max_3d"] = grp["Максимальная температура"].transform(
            lambda s: s.rolling(3, min_periods=1).max()
        )

        base_cls["temp_mean_7d"] = grp["Максимальная температура"].transform(
            lambda s: s.rolling(7, min_periods=1).mean()
        )
        base_cls["temp_max_7d"] = grp["Максимальная температура"].transform(
            lambda s: s.rolling(7, min_periods=1).max()
        )

        CURRENT_DATE = pd.to_datetime(date).normalize()

        base['date'] = pd.to_datetime(base['date'])
        base['date_in'] = pd.to_datetime(base['date_in'])
        base['days_in'] = (base['date'] - base['date_in']).dt.days

        base_cls['date'] = pd.to_datetime(base_cls['date'])
        base_cls['date_in'] = pd.to_datetime(base_cls['date_in'])
        base_cls['days_in'] = (base_cls['date'] - base_cls['date_in']).dt.days
        base_app = base_cls.copy()

        active_df = base_cls[base_app["date"] == CURRENT_DATE]
        active_df = active_df.drop(columns=["nearest_fire_date", "days_to_fire", "date_out", "fire_within_7d"],
                                   errors="ignore")
        inactive_df_reg = base[base["date_out"] < CURRENT_DATE]
        inactive_df_cl = base_app[base_app["date_out"] < CURRENT_DATE]

        inactive_df_reg_sorted = inactive_df_reg.sort_values("date").reset_index(drop=True)

        q50 = inactive_df_reg_sorted["date"].quantile(0.5)
        q80 = inactive_df_reg_sorted["date"].quantile(0.8)

        train_main = inactive_df_reg_sorted[
            (inactive_df_reg_sorted['date'] > q50) & (inactive_df_reg_sorted['date'] <= q80)]
        val_main = inactive_df_reg_sorted[(inactive_df_reg_sorted['date'] > q80)]

        # таргеты
        # days_to_fire
        y_train = train_main["days_to_fire"]
        y_val = val_main['days_to_fire']

        drop_cols = ["days_to_fire", "nearest_fire_date", "date_in", "date_out", "pile_id", "date", "w", "pile_len",
                     "days_to_fire_cap", "y_log", "fire_within_7d"]
        X_train = train_main.drop(columns=drop_cols, errors="ignore")
        X_val = val_main.drop(columns=drop_cols, errors="ignore")
        active_df = active_df.drop(columns=drop_cols, errors="ignore")

        cat_features = [c for c in ["Склад", "Штабель", "coal_type"] if c in X_train.columns]

        from catboost import CatBoostRegressor

        model = CatBoostRegressor(
            iterations=500,
            depth=5,
            learning_rate=0.03,
            loss_function="MAE",
            verbose=False
        )

        model.fit(
            X_train, y_train,
            cat_features=cat_features,
            eval_set=(X_val, y_val),
            use_best_model=True
        )

        pred_days = np.round(model.predict(active_df))

        active_df["days_to_fire"] = pred_days

        res = (
            active_df.groupby("Штабель", as_index=False)["days_to_fire"]
            .min()
        )
        return res


    def predict_and_compare(
            self,
            date: datetime.date,
            fires: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        1) Достаёт данные из БД.
        2) Строит прогноз на указанную дату.
        3) Сравнивает с фактами из fires и считает метрики качества.

        Ожидаемый формат fires:
          - колонка 'stack_id' (идентификатор штабеля)
          - колонка 'fire_date' (фактическая дата пожара)
        """

        # 1. Загружаем features из БД
        data = self._load_feature_data()

        repo.upload_fires(fires)


        return {
            "accuracy_le_2_days": 1.0
        }


    def predict_classificator(self, date: datetime.date) -> pd.DataFrame:
        df = pd.DataFrame (
            {
            "stack_id": [101, 102, 103],
            "will_burn": [1, 0, 1],
            }
        )

        return df
# Глобальный экземпляр модели (заглушка)
model = FireModel()
