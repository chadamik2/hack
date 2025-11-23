import React from "react";
import { Link } from "react-router-dom";

function Home() {
  const cardStyle = {
    border: "1px solid #ddd",
    borderRadius: "8px",
    padding: "16px",
    marginBottom: "16px"
  };

  return (
    <div>
      <h2>Выберите функцию</h2>

      <div style={cardStyle}>
        <h3>1. Загрузить текущие данные о хранении угля</h3>
        <p>
          Загрузка файлов <code>supplies.csv</code>,
          <code>weather_*.csv</code>, <code>temperature.csv</code> в базу данных.
        </p>
        <Link to="/upload">Перейти</Link>
      </div>

      <div style={cardStyle}>
        <h3>2. Календарь самовозгорания штабелей</h3>
        <p>
          Выберите дату и получите прогноз дат самовозгорания для всех
          штабелей, которые есть в базе на этот момент.
        </p>
        <Link to="/calendar">Перейти</Link>
      </div>

      <div style={cardStyle}>
        <h3>3. Загрузить новые данные о возгорании и сравнить метрики</h3>
        <p>
          Загрузите файл фактических пожаров <code>fires.csv</code>, выберите
          дату и посмотрите метрики качества модели.
        </p>
        <Link to="/metrics">Перейти</Link>
      </div>
    </div>
  );
}

export default Home;
