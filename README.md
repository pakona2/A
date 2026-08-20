# CallMe

A mobile-first calling dashboard built with React, Vite, Firebase-ready configuration, and a Flask API scaffold.

## Run the front end

```bash
npm install
npm run dev
```

## Run the Flask API

```bash
cd backend
python -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
gunicorn --chdir .. backend.app:app
```

The API exposes `GET /api/health`, `GET/POST /api/contacts`, and `GET/POST /api/calls`. It creates a local SQLite database and seeds the initial contacts on first launch. Set `CALLME_DATABASE`, `FRONTEND_ORIGIN`, `HOST`, and `PORT` in the environment for deployment. Add Firebase web configuration to `.env` using `.env.example` as a template; the frontend uses local demo data until the API is available.

For the frontend to call a deployed API, set `VITE_API_URL` to its `/api` URL before running `npm run build`.