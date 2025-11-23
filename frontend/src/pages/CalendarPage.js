import React, { useState } from "react";
import { predictFires, predictClassifier } from "../api";

function CalendarPage() {
  const [date, setDate] = useState("");
  const [regressionResult, setRegressionResult] = useState(null);   // даты пожара
  const [classifierResult, setClassifierResult] = useState(null);   // горит/не горит
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  async function handlePredict(e) {
    e.preventDefault();

    if (!date) {
      setStatus("Укажите дату");
      return;
    }

    try {
      setLoading(true);
      setStatus("");
      setRegressionResult(null);
      setClassifierResult(null);

      // параллельные запросы к обоим эндпоинтам
      const [regData, clsData] = await Promise.all([
        predictFires(date),
        predictClassifier(date)
      ]);

      setRegressionResult(regData);
      setClassifierResult(clsData);
    } catch (err) {
      setStatus(`Ошибка: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2>Календарь самовозгорания штабелей</h2>

      <form onSubmit={handlePredict} style={{ marginBottom: "16px" }}>
        <label>
          Дата прогноза:{" "}
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
          />
        </label>
        <button
          type="submit"
          disabled={loading || !date}
          style={{ marginLeft: "8px" }}
        >
          Предсказать
        </button>
      </form>

      {loading && <p>Загрузка...</p>}
      {status && <p>{status}</p>}

      {/* Таблица 1: прогноз дат самовозгорания (как было раньше) */}
      {regressionResult && (
        <div style={{ marginTop: "24px" }}>
          <h3>Прогноз дат самовозгорания для {regressionResult.input_date}</h3>

          {regressionResult.predictions &&
          Object.keys(regressionResult.predictions).length > 0 ? (
            <table
              border="1"
              cellPadding="4"
              style={{ borderCollapse: "collapse" }}
            >
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
            <p>Нет предсказаний.</p>
          )}
        </div>
      )}

      {/* Таблица 2: классификатор на 7 дней */}
      {classifierResult && (
        <div style={{ marginTop: "24px" }}>
          <h3>
            Классификатор: загорится ли штабель в ближайшие 7 дней
            (относительно {classifierResult.input_date})
          </h3>

          {classifierResult.predictions &&
          Object.keys(classifierResult.predictions).length > 0 ? (
            <table
              border="1"
              cellPadding="4"
              style={{ borderCollapse: "collapse" }}
            >
              <thead>
                <tr>
                  <th>Штабель</th>
                  <th>Загорится в ближайшие 7 дней?</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(classifierResult.predictions).map(
                  ([stackId, willBurn]) => (
                    <tr key={stackId}>
                      <td>{stackId}</td>
                      <td>{willBurn ? "Да" : "Нет"}</td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          ) : (
            <p>Нет данных классификатора.</p>
          )}
        </div>
      )}
    </div>
  );
}

export default CalendarPage;
