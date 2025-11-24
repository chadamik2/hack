# api/routes_predict.py
from datetime import datetime, date
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Query
from ml.model import FireModel, model  # адаптируй имя под свой класс
import pandas as pd

router = APIRouter(prefix="/predict", tags=["predict"])

# Один экземпляр модели на все запросы


def _serialize_predictions(pred: Dict[Any, Any]) -> Dict[str, str]:
    """
    model.predict(date) -> {stack_id: fire_date}
    Приводим к JSON-дружелюбному виду: ключи -> str, даты -> ISO-строки.
    """
    result: Dict[str, str] = {}

    for stack_id, fire_dt in pred.items():
        # ключи в строку
        key = str(stack_id)

        # значения (даты) в ISO-строку
        if isinstance(fire_dt, (datetime, date)):
            value = fire_dt.isoformat()
        else:
            value = str(fire_dt)

        result[key] = value

    return result


@router.get("/fires")
def predict_fires(
    date_str: str = Query(..., alias="date", description="Дата в формате YYYY-MM-DD"),
):
    """
    По переданной дате запускает model.predict(date) и возвращает
    словарь {штабель: дата_пожара}.
    """

    # Парсим дату
    try:
        target_date = datetime.fromisoformat(date_str).date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Неверный формат даты. Ожидается YYYY-MM-DD.",
        )

    # Вызываем модель
    raw_predictions = model.predict(target_date)

    # Приводим к JSON-формату
    pr = (
    raw_predictions
    .set_index('Штабель')['days_to_fire']
    .dt.strftime('%Y-%m-%d')
    .to_dict()
    )

    predictions = _serialize_predictions(pr)

    return {
        "input_date": target_date.isoformat(),
        "predictions": predictions,
    }



def _serialize_classification_predictions(pred: Dict[Any, Any]) -> Dict[str, bool]:
    """
    Для model.predict_classificator(date): {stack_id: bool/0/1}
    -> {str(stack_id): bool}
    """
    result: Dict[str, bool] = {}
    for stack_id, v in pred.items():
        key = str(stack_id)
        # приводим к bool: True/False
        value = bool(v)
        result[key] = value
    return result

@router.get("/classifier")
def predict_classifier(
    date_str: str = Query(..., alias="date", description="Дата в формате YYYY-MM-DD"),
):
    """
    Классификатор: для каждого штабеля предсказывает,
    загорится ли он в ближайшие 7 дней (True/False).
    """
    try:
        target_date: date = datetime.fromisoformat(date_str).date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Неверный формат даты. Ожидается YYYY-MM-DD.",
        )

    pr = model.predict_classificator(target_date)
    # модель уже реализована в FireModel
    raw_predictions = (
        pr.set_index("stack_id")           # делаем stack_id индексом
        ["will_burn"]                    # берём колонку с признаком
        .astype(bool)                    # приводим к bool (1/0 -> True/False)
        .to_dict()                       # -> {stack_id: bool}
    )

    # ожидаем dict-like {stack_id: bool/0/1}
    if not isinstance(raw_predictions, dict):
        raise HTTPException(
            status_code=500,
            detail="predict_classificator должен возвращать словарь {stack_id: bool}",
        )

    predictions = _serialize_classification_predictions(raw_predictions)

    return {
        "input_date": target_date.isoformat(),
        "predictions": predictions,  # { "101": true, "102": false, ... }
    }