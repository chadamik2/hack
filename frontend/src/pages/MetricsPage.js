import React, { useState } from "react";
import { evaluateFires } from "../api";

function MetricsPage() {
  const [date, setDate] = useState("");
  const [firesFile, setFiresFile] = useState(null);

  const [status, setStatus] = useState("");
  const [statusType, setStatusType] = useState("ok");
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();

    if (!date) {
      setStatusType("error");
      setStatus("Укажите дату прогноза.");
      return;
    }
    if (!firesFile) {
      setStatusType("error");
      setStatus("Выберите файл fires.csv.");
      return;
    }

    try {
      setStatus("");
      setLoading(true);
      setMetrics(null);

      const data = await evaluateFires(date, firesFile);
      setMetrics(data);
      setStatusType("ok");
      setStatus("Метрики успешно рассчитаны.");
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
          <div className="card-icon">📊</div>
          <div>
            <h2 className="card-title">Оценка качества модели</h2>
            <p className="card-description">
              Загрузите реальные данные о пожарах и сравните их с предсказаниями
              модели. Сейчас backend возвращает метрику{" "}
              <code>accuracy_le_2_days</code> — долю штабелей, для которых
              предсказанная дата попала в окно ±2 дня от факта.
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="card-footer">
          <div className="form-row">
            <span className="form-label">Дата прогноза:</span>
            <input
              className="input-date"
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />
          </div>
          <div className="form-row">
            <span className="form-label">Файл fires.csv:</span>
            <input
              className="input-file"
              type="file"
              accept=".csv"
              onChange={(e) => setFiresFile(e.target.files[0] || null)}
            />
          </div>
          <button type="submit" className="btn" disabled={loading}>
            {loading ? "Считаем..." : "Рассчитать метрики"}
          </button>
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

      {metrics && (
        <div className="card">
          <div className="card-header">
            <div className="card-icon">✅</div>
            <div>
              <h3 className="card-title">Результаты</h3>
              <p className="card-description">
                Основная метрика — попадание в интервал ±2 дня между фактом и
                предсказанием.
              </p>
            </div>
          </div>

          <div className="card-footer">
            <p className="text-muted">
              Accuracy (≤ 2 дня):{" "}
              <strong>
                {metrics.accuracy_le_2_days !== undefined &&
                metrics.accuracy_le_2_days !== null
                  ? Number(metrics.accuracy_le_2_days).toFixed(3)
                  : "нет данных"}
              </strong>
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default MetricsPage;
