import React, { useState } from "react";
import { predictFires, predictClassifier } from "../api";

function CalendarPage() {
  const [date, setDate] = useState("");
  const [regressionResult, setRegressionResult] = useState(null);
  const [classifierResult, setClassifierResult] = useState(null);
  const [status, setStatus] = useState("");
  const [statusType, setStatusType] = useState("ok");
  const [loading, setLoading] = useState(false);

  async function handlePredict(e) {
    e.preventDefault();

    if (!date) {
      setStatusType("error");
      setStatus("Укажите дату.");
      return;
    }

    try {
      setLoading(true);
      setStatus("");
      setRegressionResult(null);
      setClassifierResult(null);

      const [regData, clsData] = await Promise.all([
        predictFires(date),
        predictClassifier(date)
      ]);

      setRegressionResult(regData);
      setClassifierResult(clsData);
    } catch (err) {
      setStatusType("error");
      setStatus(`Ошибка: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div className="card" style={{ marginBottom: 16 }}>
        <div className="card-header">
          <div className="card-icon">📅</div>
          <div>
            <h2 className="card-title">Календарь самовозгорания штабелей</h2>
            <p className="card-description">
              Модель предсказывает дату возможного самовозгорания для каждого
              штабеля, а также даёт бинарный ответ: загорится ли куча в
              ближайшие 7 дней.
            </p>
          </div>
        </div>

        <form onSubmit={handlePredict} className="card-footer">
          <div className="form-row">
            <span className="form-label">Дата прогноза:</span>
            <input
              className="input-date"
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />
            <button
              type="submit"
              className="btn"
              disabled={loading || !date}
            >
              {loading ? "Считаем..." : "Предсказать"}
            </button>
          </div>
          <p className="text-muted">
            Используется вся информация в базе на выбранную дату.
          </p>
        </form>
      </div>

      {status && (
        <p
          className={
            "text-status " + (statusType === "error" ? "error" : "ok")
          }
        >
          {status}
        </p>
      )}

      {/* Таблица 1: прогноз дат самовозгорания */}
      {regressionResult && (
        <div className="card">
          <div className="card-header">
            <div className="card-icon">🔥</div>
            <div>
              <h3 className="card-title">
                Прогноз дат самовозгорания — {regressionResult.input_date}
              </h3>
              <p className="card-description">
                Для каждого штабеля указана дата, когда модель ожидает
                самовозгорание.
              </p>
            </div>
          </div>

          <div className="table-wrapper">
            {regressionResult.predictions &&
            Object.keys(regressionResult.predictions).length > 0 ? (
              <table className="table">
                <thead>
                  <tr>
                    <th>Штабель</th>
                    <th>Дата самовозгорания</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(regressionResult.predictions).map(
                    ([stackId, fireDate]) => (
                      <tr key={stackId}>
                        <td>{stackId}</td>
                        <td>{fireDate}</td>
                      </tr>
                    )
                  )}
                </tbody>
              </table>
            ) : (
              <p className="text-muted">Нет предсказаний для указанной даты.</p>
            )}
          </div>
        </div>
      )}

      {/* Таблица 2: классификатор на 7 дней */}
      {classifierResult && (
        <div className="card">
          <div className="card-header">
            <div className="card-icon">⚠️</div>
            <div>
              <h3 className="card-title">
                Классификатор: загорится ли куча в ближайшие 7 дней
              </h3>
              <p className="card-description">
                Значение <strong>«Да»</strong> означает, что модель ожидает
                самовозгорание в течение ближайших 7 дней, считая от{" "}
                {classifierResult.input_date}.
              </p>
            </div>
          </div>

          <div className="table-wrapper">
            {classifierResult.predictions &&
            Object.keys(classifierResult.predictions).length > 0 ? (
              <table className="table">
                <thead>
                  <tr>
                    <th>Штабель</th>
                    <th>Прогноз</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(classifierResult.predictions).map(
                    ([stackId, willBurn]) => (
                      <tr key={stackId}>
                        <td>{stackId}</td>
                        <td>
                          {willBurn ? (
                            <span className="badge badge-danger">Да</span>
                          ) : (
                            <span className="badge badge-success">Нет</span>
                          )}
                        </td>
                      </tr>
                    )
                  )}
                </tbody>
              </table>
            ) : (
              <p className="text-muted">
                Нет данных классификатора для указанной даты.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default CalendarPage;
