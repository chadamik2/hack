# Аналитика самовозгорания угля

Проект для анализа и прогнозирования самовозгорания угольных штабелей на открытых складах.

Функциональность:

1. **Загрузка текущих данных**  
   - `supplies.csv` — складские операции и остатки по штабелям  
   - `temperature.csv` — температура внутри штабелей  
   - `weather_*.csv` — погодные данные

2. **Календарь самовозгорания штабелей**  
   - Прогноз даты самовозгорания для каждого активного штабеля на выбранную дату  
   - Классификатор: загорится ли штабель в течение ближайших 7 дней

3. **Оценка качества модели**  
   - Загрузка фактических возгораний `fires.csv`  
   - Расчёт accuracy попадания в окно ±2 дня между фактом и предсказанием

---

## Стек

- **Backend**: Python, FastAPI, SQLAlchemy, Pandas, CatBoost, SQLite
- **Frontend**: React + JavaScript (Create React App)
- **Контейнеризация**: Docker, docker compose

---

## Структура репозитория

```text
.
├── backend/
│   ├── api/              # FastAPI роуты
│   ├── core/             # конфиг, подключение к БД
│   ├── data/             # репозиторий для БД
│   ├── ml/               # FireModel (обучение/предсказания)
│   ├── app.py            # точка входа FastAPI
│   ├── db.sqlite3        # база данных (SQLite)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
├── frontend/
│   ├── src/              # React-компоненты
│   ├── package.json
│   ├── Dockerfile
│   └── .dockerignore
├── docker-compose.yml
├── Презентация решения.pdf
├── data_science.ipynb
└── README.md
````

# Инструкция по запуску

Вариант 1 (через Docker):
**Проверьте, установлен ли у вас docker**

```bash
# в корне репозитория
docker compose -p hakaton up --build

# фронт:  http://localhost:3000
# бэк:    http://localhost:8000/docs
```

Вариант 2 (без Docker):

## Предварительные требования

Для запуска **без Docker** на машине должны быть установлены:

- **Python 3.10+** (вместе с `pip`)
- **Node.js 16+** и **npm** (ставятся одним установщиком с nodejs.org)
- (опционально) **Git** — для клонирования репозитория с GitHub

Проверка:

```bash
python --version
pip --version
node --version
npm --version
```


```bash
# backend
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# frontend (новый терминал)
cd frontend
npm install
npm start
```

# Как пользоваться приложением

0. Посмотреть отчет по анализу данных и тестированию моделей: приложенный файл data_science.ipynb
1. Открыть фронтенд: `http://localhost:3000`
2. На главной странице доступны три блока:

   * **Загрузить текущие данные**
     Переход на страницу загрузки `supplies.csv`, `temperature.csv`, `weather_*.csv`.
     Данные сохраняются в `db.sqlite3`.
   * **Календарь самовозгорания**
     Ввод даты → отображается:

     * прогноз даты самовозгорания по штабелям;
     * бинарный прогноз «загорится в ближайшие 7 дней» по каждому штабелю.
   * **Метрики модели**
     Загрузка `fires.csv` и выбор даты → выводится метрика `accuracy_le_2_days`.
