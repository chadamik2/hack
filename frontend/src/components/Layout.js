import React from "react";
import { NavLink } from "react-router-dom";

function Layout({ children }) {
  return (
    <div className="app-root">
      <header className="app-header">
        <h1 className="app-header-title">Аналитика самовозгорания угля</h1>
        <p className="app-header-subtitle">
          Загрузка данных, прогноз самовозгораний и оценка качества модели
        </p>

        <nav className="app-nav">
          <NavLink className="app-nav-link" to="/">
            Главная
          </NavLink>
          <NavLink className="app-nav-link" to="/upload">
            Загрузить данные
          </NavLink>
          <NavLink className="app-nav-link" to="/calendar">
            Календарь
          </NavLink>
          <NavLink className="app-nav-link" to="/metrics">
            Метрики
          </NavLink>
        </nav>
      </header>

      <main className="app-main">{children}</main>
    </div>
  );
}

export default Layout;
