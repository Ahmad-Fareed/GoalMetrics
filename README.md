<p align="center">
  <strong>⚽ GoalMetrics</strong><br>
  <em>International Football Analytics Dashboard</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/flask-3.x-000000?logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/mysql-8.x-4479A1?logo=mysql&logoColor=white" alt="MySQL">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
</p>

---

## 📖 Overview

**GoalMetrics** is a full-stack web application that lets you explore international football (soccer) data through three analytical lenses:

| Feature | Description |
|---------|-------------|
| **Head-to-Head** | Compare two national teams and view their complete historical rivalry — wins, losses, draws. |
| **Team Stats** | Dive into a team's record across every tournament they've ever competed in. |
| **Player Career** | Look up any international goalscorer's career — total goals, penalties, own goals, broken down by national team. |

The backend ingests real CSV match & goalscorer datasets into MySQL, exposes a clean REST API, and serves a premium dark-themed dashboard built with Jinja2 templates and vanilla CSS.

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                        Browser (Client)                        │
│   index.html  ·  compare.html  ·  team.html  ·  player.html   │
└──────────────────────────┬─────────────────────────────────────┘
                           │  fetch() AJAX
                           ▼
┌──────────────────────────────────────────────────────────┐
│                    Flask Application                      │
│                                                          │
│  routes/              services/              db.py       │
│  ├─ views.py          ├─ match_service.py    └─ pool +   │
│  ├─ compare.py        └─ player_service.py     context   │
│  ├─ team.py                                    manager   │
│  └─ player.py                                            │
└──────────────────────────┬───────────────────────────────┘
                           │  MySQL Connector (pool_size=5)
                           ▼
┌──────────────────────────────────────────────────────────┐
│                    MySQL Database                         │
│                                                          │
│  goalmetric_db                                           │
│  ├─ matches       (47 000+ international match results)  │
│  └─ goalscorers   (individual goal events per match)     │
└──────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
GoalMetrics/
├── app/
│   ├── __init__.py            # Application factory (create_app)
│   ├── db.py                  # MySQL pool + context manager
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── views.py           # Template-serving routes
│   │   ├── compare.py         # /api/compare
│   │   ├── team.py            # /api/team/all-tournaments
│   │   └── player.py          # /api/player/stats
│   ├── services/
│   │   ├── __init__.py
│   │   ├── match_service.py   # Head-to-head & tournament queries
│   │   └── player_service.py  # Player goal aggregation queries
│   ├── static/
│   │   └── css/
│   │       └── style.css      # Design system (dark glassmorphism theme)
│   └── templates/
│       ├── base.html          # Jinja2 base layout
│       ├── index.html         # Landing page
│       ├── compare.html       # Team comparison page
│       ├── team.html          # Team stats page
│       └── player.html        # Player stats page
├── scripts/
│   ├── pipeline.py            # DB schema + CSV ingestion pipeline
│   ├── results.csv            # Raw match results dataset
│   └── goalscorers.csv        # Raw goalscorer events dataset
├── config.py                  # Flask config classes (Dev / Test / Prod)
├── run.py                     # Entry point
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (git-ignored)
└── .gitignore
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **MySQL 8.x** (or MariaDB) running locally
- **pip** (Python package manager)

### 1 · Clone the repository

```bash
git clone https://github.com/Ahmad-Fareed/GoalMetrics.git
cd GoalMetrics
```

### 2 · Create a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3 · Install dependencies

```bash
pip install -r requirements.txt
```

### 4 · Configure environment variables

Create a `.env` file in the project root (a template is shown below):

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=goalmetric_db
```

### 5 · Run the data pipeline

This creates the database, tables, and imports the CSV datasets:

```bash
python scripts/pipeline.py
```

### 6 · Start the Flask server

```bash
python run.py
```

Open your browser at **http://localhost:5000** and start exploring!

---

## 🔌 API Reference

All endpoints return JSON.

| Method | Endpoint | Query Params | Description |
|--------|----------|-------------|-------------|
| `GET` | `/api/health` | — | Health check / liveness probe |
| `GET` | `/api/compare` | `team1`, `team2` | Head-to-head stats between two teams |
| `GET` | `/api/team/all-tournaments` | `team` | Team record grouped by tournament |
| `GET` | `/api/player/stats` | `name` | Player career goalscoring stats |

### Example Request

```bash
curl "http://localhost:5000/api/compare?team1=Brazil&team2=Argentina"
```

### Example Response

```json
{
  "team1": "Brazil",
  "team2": "Argentina",
  "total_matches": 109,
  "team1_wins": 46,
  "team2_wins": 40,
  "draws": 23
}
```

---

## 🗄️ Database Schema

### `matches`

| Column | Type | Notes |
|--------|------|-------|
| `id` | `INT` AUTO_INCREMENT | Primary key |
| `match_date` | `DATE` | Match date |
| `home_team` | `VARCHAR(100)` | Indexed |
| `away_team` | `VARCHAR(100)` | Indexed |
| `home_score` | `INT` | — |
| `away_score` | `INT` | — |
| `tournament` | `VARCHAR(150)` | — |
| `city` | `VARCHAR(100)` | — |
| `country` | `VARCHAR(100)` | — |
| `neutral_venue` | `BOOLEAN` | — |

### `goalscorers`

| Column | Type | Notes |
|--------|------|-------|
| `id` | `INT` AUTO_INCREMENT | Primary key |
| `match_date` | `DATE` | — |
| `home_team` | `VARCHAR(100)` | — |
| `away_team` | `VARCHAR(100)` | — |
| `scoring_team` | `VARCHAR(100)` | Indexed |
| `scorer` | `VARCHAR(100)` | Indexed |
| `minute` | `INT` | Goal minute |
| `own_goal` | `BOOLEAN` | — |
| `penalty` | `BOOLEAN` | — |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python · Flask · Jinja2 |
| **Database** | MySQL 8 (InnoDB) · Connection pooling |
| **Frontend** | HTML5 · Vanilla CSS (custom design system) · JavaScript (Fetch API) |
| **Data Pipeline** | Python · csv module · Batch INSERT |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/Ahmad-Fareed">Ahmad Fareed</a>
</p>
