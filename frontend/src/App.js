import React from "react";
import { Routes, Route } from "react-router-dom";

import Layout from "./components/Layout";
import Home from "./pages/Home";
import UploadDataPage from "./pages/UploadDataPage";
import CalendarPage from "./pages/CalendarPage";
import MetricsPage from "./pages/MetricsPage";

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/upload" element={<UploadDataPage />} />
        <Route path="/calendar" element={<CalendarPage />} />
        <Route path="/metrics" element={<MetricsPage />} />
      </Routes>
    </Layout>
  );
}

export default App;
