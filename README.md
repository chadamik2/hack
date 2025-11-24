## Инструкция по запуску проекта

### 1. Подготовка окружения

Требуется:

* Python 3.10+
* Node.js 18+
* Git (если проект в репозитории)

Клонировать репозиторий (или просто перейти в папку проекта):

```bash
cd C:\Users\Denis\Desktop\ХАКАТОН
```

---

### 2. Запуск backend (FastAPI)

1. Создать и активировать виртуальное окружение (один раз):

   ```bash
   python -m venv venv
   # PowerShell:
   .\venv\Scripts\Activate.ps1
   # или cmd:
   venv\Scripts\activate.bat
   ```

2. Установить зависимости:

   ```bash
   pip install -r requirements.txt
   ```

3. Убедиться, что в `core/config.py` указан корректный `DATABASE_URL`.
   Для локального SQLite, например:

   ```python
   DATABASE_URL = "sqlite:///./db.sqlite3"
   ```

4. Запустить сервер:

   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

   Backend будет доступен на `http://127.0.0.1:8000`, документация Swagger – `http://127.0.0.1:8000/docs`.

---

### 3. Запуск frontend (React)

В отдельном терминале:

1. Перейти в папку фронтенда:

   ```bash
   cd C:\Users\Denis\Desktop\ХАКАТОН\frontend
   ```

2. Установить зависимости (один раз):

   ```bash
   npm install
   ```

3. Запустить dev-сервер:

   ```bash
   npm start
   ```

   Frontend будет доступен на `http://localhost:3000`.

---

### 4. Взаимодействие фронта и бэка

В `src/api.js` фронтенд ожидает backend по адресу:

```javascript
const API_BASE_URL = "http://localhost:8000";
```

В `app.py` должно быть подключено CORS (чтобы разрешить запросы от фронта):

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

После этого:

* загрузка CSV работает через страницы:

  * «Загрузить текущие данные о хранении угля»
  * «Загрузить новые данные о возгорании и сравнить метрики»
* прогнозы и классификатор доступны на странице «Календарь самовозгорания штабелей».
