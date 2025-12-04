# How to Run Energy Trading Operations Suite

## Location
The project is located at:
`/Users/mozy_uk/.gemini/antigravity/scratch`

## 1. Start the Backend (FastAPI)
Open a terminal and run:

```bash
cd /Users/mozy_uk/.gemini/antigravity/scratch/backend
source venv/bin/activate
uvicorn main:app --reloadcd /Users/mozy_uk/.gemini/
```

*The backend will run on http://localhost:8000*

## 2. Start the Frontend (Next.js)
Open a **new** terminal window and run:

```bash
cd /Users/mozy_uk/.gemini/antigravity/scratch/frontend
npm run dev
```

*The frontend will run on http://localhost:3000*

## 3. Open the App
Go to [http://localhost:3000](http://localhost:3000) in your browser.
