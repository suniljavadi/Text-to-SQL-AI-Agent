$env:PYTHONPATH = (Get-Location).Path
python database/seed_data.py
uvicorn app.main:app --reload
