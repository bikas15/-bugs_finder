# Bugs Finder

React frontend and Django REST API for code analysis, account sign-in, and user-owned reports.

## Local development

1. Install the backend requirements and configure local settings:

   ```powershell
   cd bugsfinder
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   Copy-Item .env.example .env
   python manage.py migrate
   python manage.py runserver
   ```

   Local email uses Django's console backend; activation links appear in the Django terminal. Set `GEMINI_API_KEY` in `bugsfinder\.env` for AI analysis.
2. In a separate terminal, install and start React:

   ```powershell
   Copy-Item .env.example .env
   npm ci
   npm start
   ```

## Deploy

The GitHub Pages workflow builds the frontend with the public Render API URL. The `render.yaml` Blueprint creates a Django service and a free Render PostgreSQL database. In Render, create a **Blueprint Instance** from this repository and confirm the free resources.

After the backend is created, add these private service environment variables in Render:

- `EMAIL_HOST_USER`: the sender email address.
- `EMAIL_HOST_PASSWORD`: an SMTP/app password (never a regular account password).
- `GEMINI_API_KEY`: a server-side Gemini API key.

Do not put these secrets in GitHub files or frontend variables. Sign-up will return a clear service error until SMTP is configured; AI analysis needs the Gemini key.

The free Render web service can sleep, and free PostgreSQL is temporary rather than production storage. The database may expire and its contents may be deleted; upgrade to a paid database before relying on long-term accounts or reports. Accounts in this hosted database are separate from local SQLite accounts.
