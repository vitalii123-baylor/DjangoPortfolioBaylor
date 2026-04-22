@echo off
echo ============================================
echo   Smart Financial Decision Maker — Setup
echo ============================================

set GEMINI_API_KEY=AIzaSyB35Jog4pEYINuMKoOKF8tn1Z3mLJ-sWPM

echo.
echo [1/5] Installing dependencies...
pip install -r requirements.txt

echo.
echo [2/5] Creating migrations...
python manage.py makemigrations expense_tracker sentiment_analyzer

echo.
echo [3/5] Running database migrations...
python manage.py migrate

echo.
echo [4/5] Creating superuser (admin / admin123)...
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin','admin@example.com','admin123')"

echo.
echo [5/5] Collecting static files...
python manage.py collectstatic --noinput 2>nul

echo.
echo ============================================
echo   Setup complete!
echo   Login: admin / admin123
echo   Starting server at http://127.0.0.1:8000/
echo ============================================
python manage.py runserver
