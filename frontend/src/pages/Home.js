import React from "react";
import { Link } from "react-router-dom";

function Home() {
  return (
    <div>
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="card-header">
          <div className="card-icon">📦</div>
          <div>
            <h2 className="card-title">Панель управления хранилищем</h2>
            <p className="card-description">
              Выберите режим работы: загрузка входных данных, прогноз
              самовозгораний или оценка качества модели по фактическим пожарам.
            </p>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <div className="card-icon">⬆️</div>
          <div>
            <h3 className="card-title">1. Загрузить текущие данные о хранении угля</h3>
            <p className="card-description">
              Загрузите файлы <code>supplies.csv</code>, <code>weather_*.csv</code>{" "}
              и <code>temperature.csv</code> в базу данных, чтобы модель работала
              с актуальной информацией.
            </p>
          </div>
        </div>
        <div className="card-footer">
          <Link to="/upload" className="btn">
            Перейти к загрузке данных
          </Link>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <div className="card-icon">📅</div>
          <div>
            <h3 className="card-title">2. Календарь самовозгорания штабелей</h3>
            <p className="card-description">
              Выберите дату и получите прогноз по каждой куче: когда она
              загорится и загорится ли в ближайшие 7 дней.
            </p>
          </div>
        </div>
        <div className="card-footer">
          <Link to="/calendar" className="btn">
            Открыть календарь
          </Link>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <div className="card-icon">📊</div>
          <div>
            <h3 className="card-title">
              3. Загрузить фактические возгорания и сравнить метрики
            </h3>
            <p className="card-description">
              Загрузите <code>fires.csv</code>, чтобы посчитать точность модели
              (попадание в интервал ±2 дня) на реальных данных.
            </p>
          </div>
        </div>
        <div className="card-footer">
          <Link to="/metrics" className="btn">
            Перейти к метрикам
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Home;
