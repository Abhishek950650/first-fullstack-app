@echo off
echo Building Angular...
cd frontend
call ng build
echo Build complete!
cd ..
echo Starting Flask server...
cd backend
call venv\Scripts\activate
python app.py