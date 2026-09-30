# AI Classroom Monitoring System — Render Ready

This project contains a Flask web/API service plus a separate YOLO/OpenCV camera worker.

## Architecture

Browser -> Render Flask -> PostgreSQL/SQLite
                         ^
                         |
                   AI Worker PC
                         |
                     OpenCV/YOLO
                         |
                     Camera 1..25

## 1. Local setup

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Open:

- http://127.0.0.1:5000/
- http://127.0.0.1:5000/analytics
- http://127.0.0.1:5000/api/health

## 2. GitHub

```powershell
git init
git add .
git commit -m "AI classroom monitoring Render deployment"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

If the repository already has `origin`, use:

```powershell
git remote -v
git push origin main
```

## 3. Render

Create a Render Web Service from the GitHub repository.

Build command:

```text
pip install -r requirements.txt
```

Start command:

```text
gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120 app:app
```

Health check:

```text
/api/health
```

Root directory must contain `app.py`.

## 4. Environment variables

Set:

```text
WORKER_API_KEY=your-long-random-secret
```

For production PostgreSQL, add the PostgreSQL connection URL supplied by Render:

```text
DATABASE_URL=...
```

The app automatically uses PostgreSQL when DATABASE_URL exists; otherwise it uses SQLite.

## 5. AI worker

The physical cameras must be accessible to the machine running the worker. Render cannot directly open USB cameras attached to your laptop/college computer.

On the camera/AI computer:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Set:

```powershell
$env:API_URL="https://YOUR-RENDER-SERVICE.onrender.com"
$env:WORKER_API_KEY="same-secret-as-render"
```

Run camera 1:

```powershell
python worker\ai_worker.py --camera 1 --source 0 --name "Classroom Camera 1" --location "A Block"
```

Camera 2:

```powershell
python worker\ai_worker.py --camera 2 --source 1 --name "Classroom Camera 2" --location "B Block"
```

For an RTSP/HTTP source, pass the URL instead of a number:

```powershell
python worker\ai_worker.py --camera 3 --source "rtsp://USER:PASSWORD@CAMERA-IP/stream"
```

## 6. Important production notes

- SQLite is suitable for local testing. Use Render PostgreSQL for production data.
- YOLO/OpenCV processing is intentionally separated from the Render web service.
- A Render web service cannot directly access USB cameras attached to another computer.
- The worker sends detection summaries to `/api/worker/detection`.
- Set WORKER_API_KEY on both Render and the worker machine.
- Do not commit `.env` files or real passwords/API keys to GitHub.

## API endpoints

- GET `/`
- GET `/analytics`
- GET `/api/health`
- GET `/api/summary`
- GET `/api/cameras`
- GET `/api/detections?limit=50`
- GET `/api/cameras/<camera_id>`
- POST `/api/worker/detection`
- POST `/api/cameras/register`
