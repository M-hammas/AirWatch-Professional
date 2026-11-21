# AirWatch — Air Quality Monitoring System

A full-stack academic project built with React + Vite, FastAPI, SQLAlchemy, MySQL and the Open-Meteo Air Quality API.

## Features
- Register and log in with hashed passwords and JWT authentication.
- Search cities using Open-Meteo Geocoding.
- Fetch current air-quality measurements and persist timestamped readings.
- Dashboard for PM2.5, PM10, CO, NO2, SO2 and O3.
- Historical readings, pollutant averages and city comparison endpoints.
- Save favourite locations.
- Configure pollution threshold alerts.
- Responsive dashboard UI with charts and loading/error states.

## Requirements
- Python 3.11+
- Node.js 20+
- MySQL 8+
- Internet connection for Open-Meteo data

## 1. Database setup
Create a MySQL database and user (or use your own credentials):

```sql
CREATE DATABASE airwatch CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'airwatch_user'@'localhost' IDENTIFIED BY 'ChangeThisPassword!';
GRANT ALL PRIVILEGES ON airwatch.* TO 'airwatch_user'@'localhost';
FLUSH PRIVILEGES;
```

## 2. Backend setup (Windows PowerShell)
Open PowerShell in `backend`:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend/.env` and set your MySQL password and a long random `SECRET_KEY`.

Run the API:

```powershell
uvicorn app.main:app --reload
```

API: http://127.0.0.1:8000  
Interactive API docs: http://127.0.0.1:8000/docs

Tables are created automatically at startup for this student project. For production, use Alembic migrations.

## 3. Frontend setup
Open a second PowerShell terminal in `frontend`:

```powershell
npm install
Copy-Item .env.example .env
npm run dev
```

Open the URL printed by Vite (normally http://localhost:5173).

## 4. First use
1. Register an account.
2. Search for a city such as `Lahore`, `Karachi` or `Chishtian`.
3. Open a result and select **Monitor**.
4. The backend fetches the latest available hourly data from Open-Meteo and stores it in MySQL.
5. Visit History, Analytics, Saved Cities and Alerts.

## Project structure
```text
AirWatch_Professional/
├── backend/
│   ├── app/
│   │   ├── routers/       # auth, cities, readings, alerts
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── security.py
│   │   └── main.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── .env.example
├── database/
│   └── schema.sql
└── docs/
    ├── DATABASE_DESIGN.md
    ├── API_GUIDE.md
    └── PRESENTATION_GUIDE.md
```

## Important notes
- Open-Meteo provides modelled air-quality data, not a guarantee of a physical monitoring-station measurement at every coordinate.
- AQI is not fabricated when unavailable. The interface displays the available pollutant measurements.
- Never commit `.env`, database passwords, or JWT secrets to GitHub.
- This is an educational project foundation. Before public deployment, add Alembic migrations, HTTPS, stronger rate limiting, email verification, backups, monitoring and production secret management.
