# FitBuddy – AI Fitness Plan Generator

FitBuddy is a FastAPI + Jinja2 + SQLite web application that uses Google Gemini to create a structured 7-day wellness/workout plan, a nutrition/recovery tip, and an updated plan from user feedback.

## Architecture

- Frontend: HTML + Jinja2 + responsive CSS
- Backend: FastAPI
- AI: Google GenAI Python SDK
- Workout generation: Gemini 3.1 Pro Preview
- Nutrition/recovery tip: Gemini 3.6 Flash
- Database: SQLite + SQLAlchemy
- API docs: FastAPI Swagger UI at `/docs`

## Project structure

```text
FitBuddy/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── gemini_client.py
│   ├── gemini_generator.py
│   ├── gemini_flash_generator.py
│   ├── updated_plan.py
│   └── routes.py
├── templates/
│   ├── index.html
│   ├── result.html
│   └── all_users.html
├── static/
│   └── css/
│       └── style.css
├── tests/
│   └── test_app.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Windows + VS Code setup

### 1. Open the project

In VS Code, choose **File → Open Folder** and select the `FitBuddy` folder.

### 2. Open the terminal

Use **Terminal → New Terminal**.

### 3. Create a virtual environment

```powershell
python -m venv venv
```

### 4. Activate it

```powershell
venv\Scripts\activate
```

If PowerShell blocks activation, use:

```powershell
venv\Scripts\python.exe -m pip install -r requirements.txt
```

and run Uvicorn with:

```powershell
venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

### 5. Install packages

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 6. Create `.env`

Copy `.env.example` and rename the copy to:

```text
.env
```

Then put your Gemini API key in:

```text
GEMINI_API_KEY=your_real_key_here
```

Do not upload `.env` to GitHub.

### 7. Start FitBuddy

```powershell
python -m uvicorn app.main:app --reload
```

You should see a message similar to:

```text
Uvicorn running on http://127.0.0.1:8000
```

Open:

- Home: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs
- Admin dashboard: http://127.0.0.1:8000/view-all-users
- Health check: http://127.0.0.1:8000/api/health

## Testing

Run:

```powershell
python -m pytest
```

The tests verify that the homepage, health endpoint, and users API are reachable. They do not call Gemini, so a Gemini key is not required for those basic tests.

## How the application works

1. User opens `/`.
2. User enters name, user ID, age, weight, goal, and intensity.
3. `/generate-workout` validates the form.
4. Gemini Pro generates a structured 7-day plan.
5. Gemini Flash generates a concise nutrition/recovery tip.
6. User and plan data are stored in SQLite.
7. `result.html` displays the generated plan.
8. User can submit feedback.
9. `/submit-feedback` loads the original plan and sends it plus feedback to Gemini.
10. The updated plan is stored separately so the original is preserved.
11. `/view-all-users` displays stored profiles and both plan versions.

## API endpoints

### `GET /api/health`

Returns:

```json
{
  "status": "ok",
  "service": "FitBuddy"
}
```

### `GET /api/users`

Returns a list of stored user summaries.

### `GET /api/users/{user_id}`

Returns one user's profile, original plan, updated plan, tip, and feedback.

### HTML routes

- `GET /`
- `POST /generate-workout`
- `POST /submit-feedback`
- `GET /view-all-users`

## Important implementation note

The original project document specifies `google-generativeai`, Gemini 1.5 Pro, and Gemini Flash. This implementation intentionally uses the current `google-genai` SDK and current Gemini model IDs instead. The application still follows the same requested Pro-for-plans and Flash-for-tips architecture.

## Safety

FitBuddy is a demonstration/general-wellness application. It does not diagnose conditions or replace medical care. The prompts specifically avoid extreme dieting, unsafe exercise challenges, unsafe supplements, and appearance-based judgment.
