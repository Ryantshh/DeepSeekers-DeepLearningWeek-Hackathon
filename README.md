# Quickstart tutorial (Follow all steps to run via localhost)

## Frontend
1. In frontend directory, download all the stuff and run 
```
cd frontend
npm install
npm run dev
```

## Backend (cd to respective folders to run)
1. Run the chatbot microservice
```
cd Chatbot
python -m venv venv
venv/scripts/activate
pip install -r requirements.txt
python app.py
```

2. Run the mental-health-analyzer microservice
```
cd mental-health-analyzer
python -m venv venv
venv/scripts/activate
pip install -r requirements.txt
python app.py
```

3. Run the audioTranscriber microservice (fastAPI)
```
cd mental-health-analyzer
python -m venv venv
venv/scripts/activate
pip install -r requirements.txt
uvicorn main:app --port 8000
```
