# backend/ml/model.py
import datetime
from dataclasses import dataclass
from typing import Any, Dict
import pandas as pd
from data.repository import repo

from core.config import engine



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

    def train(self, supplies: pd.DataFrame,
                                 temperature: pd.DataFrame,
                                 weather: pd.DataFrame,
                                    fires: pd.DataFrame):
        pass

    def predict(self, date: datetime.date) -> pd.DataFrame:
        """
               MOCK-реализация.
               Вместо настоящих предсказаний создаёт фейковый датафрейм и
               возвращает словарь {stack_id: fire_date}.
               """

        # mock-данные: 3 штабеля и через сколько дней они "загорятся"
        df = pd.DataFrame(
            {
                "stack_id": [101, 102, 103],
                "days_to_fire": ['2021-01-08', '2021-01-10', '2021-01-15'],
            }
        )



        # превращаем в словарь {stack_id: fire_date}
        predictions: Dict[int, date] = (
            df.set_index("stack_id")["days_to_fire"].to_dict()
        )

        return predictions

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


        return {
            "accuracy_le_2_days": 1.0
        }


# Глобальный экземпляр модели (заглушка)
model = FireModel()
