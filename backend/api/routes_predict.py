from datetime import datetime, date
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Query
from ml.model import FireModel, model
import pandas as pd

router = APIRouter(prefix="/predict", tags=["predict"])


def _serialize_predictions(pred: Dict[Any, Any]) -> Dict[str, str]:
    result: Dict[str, str] = {}

    for stack_id, fire_dt in pred.items():
        key = str(stack_id)

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
    try:
        target_date = datetime.fromisoformat(date_str).date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Неверный формат даты. Ожидается YYYY-MM-DD.",
        )

    raw_predictions = model.predict(target_date)

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
    result: Dict[str, bool] = {}
    for stack_id, v in pred.items():
        key = str(stack_id)
        value = bool(v)
        result[key] = value
    return result

@router.get("/classifier")
def predict_classifier(
    date_str: str = Query(..., alias="date", description="Дата в формате YYYY-MM-DD"),
):
    try:
        target_date: date = datetime.fromisoformat(date_str).date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Неверный формат даты. Ожидается YYYY-MM-DD.",
        )

    pr = model.predict_classificator(target_date)
    raw_predictions = (
        pr.set_index("stack_id")
        ["will_burn"]
        .astype(bool)
        .to_dict()
    )

    if not isinstance(raw_predictions, dict):
        raise HTTPException(
            status_code=500,
            detail="predict_classificator должен возвращать словарь {stack_id: bool}",
        )

    predictions = _serialize_classification_predictions(raw_predictions)

    return {
        "input_date": target_date.isoformat(),
        "predictions": predictions,
    }
