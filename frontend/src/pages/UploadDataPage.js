import React, { useState } from "react";
import { uploadCsv } from "../api";

function UploadDataPage() {
  const [suppliesFile, setSuppliesFile] = useState(null);
  const [weatherFile, setWeatherFile] = useState(null);
  const [temperatureFile, setTemperatureFile] = useState(null);

  const [status, setStatus] = useState("");
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
        setStatus("Выберите файл перед загрузкой");
        return;
      }

      const response = await uploadCsv(path, file);
      setStatus(
        `Загрузка успешна: ${response.rows_added ?? "n/a"} строк добавлено`
      );
    } catch (err) {
      setStatus(`Ошибка: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  const fieldStyle = { marginBottom: "16px" };

  return (
    <div>
      <h2>Загрузить текущие данные о хранении угля</h2>

      <div style={fieldStyle}>
        <h3>supplies.csv</h3>
        <input
          type="file"
          accept=".csv"
          onChange={(e) => setSuppliesFile(e.target.files[0] || null)}
        />
        <button
          onClick={() => handleUpload("supplies")}
          disabled={loading || !suppliesFile}
          style={{ marginLeft: "8px" }}
        >
          Загрузить supplies
        </button>
      </div>

      <div style={fieldStyle}>
        <h3>weather_*.csv</h3>
        <input
          type="file"
          accept=".csv"
          onChange={(e) => setWeatherFile(e.target.files[0] || null)}
        />
        <button
          onClick={() => handleUpload("weather")}
          disabled={loading || !weatherFile}
          style={{ marginLeft: "8px" }}
        >
          Загрузить weather
        </button>
      </div>

      <div style={fieldStyle}>
        <h3>temperature.csv</h3>
        <input
          type="file"
          accept=".csv"
          onChange={(e) => setTemperatureFile(e.target.files[0] || null)}
        />
        <button
          onClick={() => handleUpload("temperature")}
          disabled={loading || !temperatureFile}
          style={{ marginLeft: "8px" }}
        >
          Загрузить temperature
        </button>
      </div>

      {loading && <p>Загрузка...</p>}
      {status && <p>{status}</p>}
    </div>
  );
}

export default UploadDataPage;
