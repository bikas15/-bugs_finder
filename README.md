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

The GitHub Pages workflow builds the frontend with the public Render API URL. The `render.yaml` Blueprint creates the Django web service. Supply an external PostgreSQL connection string as the service's private `DATABASE_URL` environment variable. The deployment can use a Neon Free project.

After the backend is created, add these private service environment variables in Render:

- `EMAIL_HOST_USER`: the sender email address.
- `EMAIL_HOST_PASSWORD`: an SMTP/app password (never a regular account password).
- `GEMINI_API_KEY`: a server-side Gemini API key.
- `BUGSFINDER_DEMO_EMAIL` and `BUGSFINDER_DEMO_PASSWORD`: optional shared demo login credentials. The password must be at least 12 characters. Anyone using this shared account can see its saved reports, so do not store private data there.

The demo deployment enables `AUTO_ACTIVATE_SIGNUPS`, so new accounts can sign in without email verification while SMTP is not configured. This does not verify that a user owns the submitted email address. Turn this off and configure SMTP before relying on verified email accounts. AI code analysis needs the private `GEMINI_API_KEY` setting.

Do not put these secrets in GitHub files or frontend variables. Code execution is proxied through Django to TIO's sandbox because Piston's public endpoint now requires authorization; submitted code and input are sent to TIO for execution. Users can save successful AI analyses or code-run output as reports.

The free Render web service and Neon compute can sleep. Neon retains data when compute scales down. Keep independent PostgreSQL backups of hosted accounts and reports. Hosted accounts are separate from local SQLite accounts.
