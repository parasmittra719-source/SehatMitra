@echo off
echo Starting SehatMitra Backend...
set USE_MOCK=true

REM Start backend in a new window
start cmd /k "cd backend && pip install -r requirements.txt && python app.py"

echo Starting SehatMitra Frontend...
REM Start frontend server
cd frontend
python -m http.server 8000
