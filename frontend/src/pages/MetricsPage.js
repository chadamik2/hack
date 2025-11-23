import React, { useState } from "react";
import { evaluateFires } from "../api";

function MetricsPage() {
  const [date, setDate] = useState("");
  const [firesFile, setFiresFile] = useState(null);

  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();

    if (!date) {
      setStatus("Укажите дату");
      return;
    }
    if (!firesFile) {
      setStatus("Выберите файл fires.csv");
      return;
    }

    try {
      setStatus("");
      setLoading(true);
      setMetrics(null);

      const data = await evaluateFires(date, firesFile);
      setMetrics(data);
    } catch (err) {
      setStatus(`Ошибка: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2>Загрузить новые данные о возгорании и сравнить метрики</h2>

      <form onSubmit={handleSubmit} style={{ marginBottom: "16px" }}>
        <div style={{ marginBottom: "8px" }}>
          <label>
            Дата прогноза:{" "}
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />
          </label>
        </div>

        <div style={{ marginBottom: "8px" }}>
          <label>
            Файл fires.csv:{" "}
            <input
              type="file"
              accept=".csv"
              onChange={(e) => setFiresFile(e.target.files[0] || null)}
            />
          </label>
        </div>

        <button type="submit" disabled={loading}>
          Рассчитать метрики
        </button>
      </form>

      {loading && <p>Загрузка...</p>}
      {status && <p>{status}</p>}

      {metrics && (
        <div>
          <h3>Результаты</h3>
          <p>
            Accuracy (попадание в интервал ≤ 2 дня):{" "}
            {metrics.accuracy_le_2_days !== undefined &&
            metrics.accuracy_le_2_days !== null
              ? Number(metrics.accuracy_le_2_days).toFixed(3)
              : "нет данных"}
          </p>
        </div>
      )}
    </div>
  );
}

export default MetricsPage;
