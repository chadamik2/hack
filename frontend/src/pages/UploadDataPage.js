import React, { useState } from "react";
import { uploadCsv } from "../api";

function UploadDataPage() {
  const [suppliesFile, setSuppliesFile] = useState(null);
  const [weatherFile, setWeatherFile] = useState(null);
  const [temperatureFile, setTemperatureFile] = useState(null);

  const [status, setStatus] = useState("");
  const [statusType, setStatusType] = useState("ok");
  const [loading, setLoading] = useState(false);

  async function handleUpload(type) {
    try {
      setStatus("");
      setLoading(true);

      let file = null;
      let path = "";

      if (type === "supplies") {
        file = suppliesFile;
        path = "/upload/supplies";
      } else if (type === "weather") {
        file = weatherFile;
        path = "/upload/weather";
      } else if (type === "temperature") {
        file = temperatureFile;
        path = "/upload/temperature";
      }

      if (!file) {
        setStatusType("error");
        setStatus("Выберите файл перед загрузкой.");
        return;
      }

      const response = await uploadCsv(path, file);
      const added = response.rows_added ?? "0";
      setStatusType("ok");
      setStatus(`Загрузка успешна: добавлено строк — ${added}.`);
    } catch (err) {
      setStatusType("error");
      setStatus(`Ошибка: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  function renderBlock(title, description, stateKey, setStateKey, type) {
    return (
      <div className="card">
        <div className="card-header">
          <div className="card-icon">
            {type === "supplies" ? "📦" : type === "weather" ? "🌦️" : "🌡️"}
          </div>
          <div>
            <h3 className="card-title">{title}</h3>
            <p className="card-description">{description}</p>
          </div>
        </div>

        <div className="card-footer">
          <div className="form-row">
            <span className="form-label">Файл:</span>
            <input
              className="input-file"
              type="file"
              accept=".csv"
              onChange={(e) => setStateKey(e.target.files[0] || null)}
            />
          </div>
          <button
            className="btn"
            onClick={() => handleUpload(type)}
            disabled={loading || !stateKey}
          >
            {loading ? "Загрузка..." : "Загрузить"}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="card-header">
          <div className="card-icon">⬆️</div>
          <div>
            <h2 className="card-title">Загрузка текущих данных</h2>
            <p className="card-description">
              Загрузите актуальные данные по складу, погоде и температуре,
              чтобы модель могла строить корректные прогнозы.
            </p>
          </div>
        </div>
      </div>

      {renderBlock(
        "supplies.csv — операции и остатки",
        "Файл с выгрузкой и отгрузкой угля по складам и штабелям.",
        suppliesFile,
        setSuppliesFile,
        "supplies"
      )}

      {renderBlock(
        "weather_*.csv — погодные данные",
        "Файл с погодными наблюдениями (температура воздуха, осадки и т.д.).",
        weatherFile,
        setWeatherFile,
        "weather"
      )}

      {renderBlock(
        "temperature.csv — температура в штабелях",
        "Файл с данными по температуре внутри штабелей.",
        temperatureFile,
        setTemperatureFile,
        "temperature"
      )}

      {status && (
        <p
          className={
            "text-status " + (statusType === "error" ? "error" : "ok")
          }
        >
          {status}
        </p>
      )}
    </div>
  );
}

export default UploadDataPage;
