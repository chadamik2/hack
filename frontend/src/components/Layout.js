import React from "react";
import { Link } from "react-router-dom";

function Layout({ children }) {
  return (
    <div style={{ fontFamily: "sans-serif", padding: "20px" }}>
      <header style={{ marginBottom: "20px" }}>
        <h1>Аналитика самовозгорания угля</h1>
        <nav style={{ marginTop: "10px", marginBottom: "10px" }}>
          <Link to="/" style={{ marginRight: "15px" }}>
            Главная
          </Link>
          <Link to="/upload" style={{ marginRight: "15px" }}>
            Загрузить данные
          </Link>
          <Link to="/calendar" style={{ marginRight: "15px" }}>
            Календарь
          </Link>
          <Link to="/metrics">
            Метрики
          </Link>
        </nav>
        <hr />
      </header>

      <main>{children}</main>
    </div>
  );
}

export default Layout;
