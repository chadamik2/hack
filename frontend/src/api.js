const API_BASE_URL = "http://localhost:8000";

export async function uploadCsv(path, file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    body: formData
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Ошибка загрузки файла");
  }

  return res.json();
}

export async function predictFires(dateString) {
  const res = await fetch(
    `${API_BASE_URL}/predict/fires?date=${encodeURIComponent(dateString)}`
  );

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Ошибка предсказания");
  }

  return res.json();
}

export async function evaluateFires(dateString, firesFile) {
  const formData = new FormData();
  formData.append("file", firesFile);

  const res = await fetch(
    `${API_BASE_URL}/metrics/fires?date=${encodeURIComponent(dateString)}`,
    {
      method: "POST",
      body: formData
    }
  );

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Ошибка оценки метрик");
  }

  return res.json();
}

export async function predictClassifier(dateString) {
  const res = await fetch(
    `${API_BASE_URL}/predict/classifier?date=${encodeURIComponent(dateString)}`
  );

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Ошибка классификации");
  }

  return res.json();
}
