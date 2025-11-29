import os
import shutil
import tempfile
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Google Calendar OAuth
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Import your existing agent logic
from campus_taskflow.adk.core import State
from campus_taskflow.agents.orchestrator import OrchestratorAgent
from campus_taskflow.tools.search_tools import EmbeddingSearchTool
from campus_taskflow.adk.skills import LLMSkill

# Allow OAuth over HTTP for local dev
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
REDIRECT_URI = 'http://localhost:8000/api/auth/callback'

app = FastAPI(title="ScholarFlow AI API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all. In production, specify the frontend URL.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []

class ChatResponse(BaseModel):
    response: str

class SettingsRequest(BaseModel):
    api_key: str

# --- Global State (Simple in-memory for demo purposes) ---
class GlobalStore:
    last_state: Optional[State] = None
    history: List[dict] = []
    credentials: Optional[dict] = None
    chat_history: List[dict] = []

store = GlobalStore()

# --- Endpoints ---

@app.get("/")
def read_root():
    return {"message": "ScholarFlow AI API is running"}

@app.get("/api/history")
def get_history():
    return store.history

@app.post("/api/settings")
async def set_settings(settings: SettingsRequest):
    if settings.api_key:
        os.environ["GOOGLE_API_KEY"] = settings.api_key
        return {"status": "success", "message": "API Key set successfully"}
    raise HTTPException(status_code=400, detail="API Key is required")

# --- OAuth Endpoints ---
@app.get("/api/auth/login")
def login():
    if not os.path.exists(CLIENT_SECRETS_FILE):
        raise HTTPException(status_code=400, detail="client_secret.json not found. Please add it to the project root.")
    
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, redirect_uri=REDIRECT_URI)
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')
    
    return {"url": authorization_url}

@app.get("/api/auth/callback")
def callback(code: str):
    if not os.path.exists(CLIENT_SECRETS_FILE):
        raise HTTPException(status_code=400, detail="client_secret.json not found.")

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, redirect_uri=REDIRECT_URI)
    
    flow.fetch_token(code=code)
    credentials = flow.credentials
    
    store.credentials = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    return {"message": "Authentication successful! You can close this window."}

@app.post("/api/calendar/add")
def add_calendar_event(event: dict = Body(...)):
    if not hasattr(store, 'credentials') or not store.credentials:
         raise HTTPException(status_code=401, detail="User not authenticated. Please connect Google Calendar first.")

    creds = Credentials(**store.credentials)
    service = build('calendar', 'v3', credentials=creds)

    date_str = event.get('date')
    summary = event.get('task', 'Study Session')
    
    event_body = {
        'summary': summary,
        'description': f"Study session for: {summary}",
        'start': {
            'date': date_str,
            'timeZone': 'UTC',
        },
        'end': {
            'date': date_str,
            'timeZone': 'UTC',
        },
    }

    try:
        event = service.events().insert(calendarId='primary', body=event_body).execute()
        return {"message": "Event created", "link": event.get('htmlLink')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name

        orchestrator = OrchestratorAgent()
        state = State()

        print(f"Processing {file.filename}...")
        orchestrator.run(state, tmp_path)
        
        store.last_state = state
        
        history_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "filename": file.filename,
            "summary": state.get("summary", {}).get("summary", "No summary"),
            "tasks_count": len(state.get("parsed_tasks", [])),
            "flashcards_count": len(state.get("flashcards", [])),
            "schedule_count": len(state.get("schedule", []))
        }
        store.history.append(history_entry)
        
        os.unlink(tmp_path)
        
        return {
            "status": "success",
            "summary": state.get("summary", {}),
            "tasks": state.get("parsed_tasks", []),
            "schedule": state.get("schedule", []),
            "flashcards": state.get("flashcards", [])
        }

    except Exception as e:
        print(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard")
def get_dashboard_data():
    if not store.last_state:
        return {"status": "empty", "message": "No data available. Please upload a file first."}
    
    state = store.last_state
    return {
        "status": "success",
        "summary": state.get("summary", {}),
        "tasks": state.get("parsed_tasks", []),
        "schedule": state.get("schedule", []),
        "flashcards": state.get("flashcards", [])
    }

@app.get("/api/chat/history")
def get_chat_history():
    """
    Returns the current session's chat history.
    """
    return store.chat_history

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not store.last_state:
         return ChatResponse(response="Please upload and analyze a document first so I can answer questions about it.")

    prompt = request.message
    
    # Add user message to history
    store.chat_history.append({"role": "user", "content": prompt})
    
    try:
        rag_tool = EmbeddingSearchTool()
        results = rag_tool.run(prompt)
        
        if results:
            context = "\n".join([r['content'] for r in results])
            llm = LLMSkill()
            full_prompt = f"Answer the question based on the context:\nContext: {context}\nQuestion: {prompt}"
            answer = llm.execute(full_prompt)
        else:
            answer = "I couldn't find relevant information in the document."
        
        # Add assistant message to history
        store.chat_history.append({"role": "assistant", "content": answer})
            
        return ChatResponse(response=answer)

    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Static Files (Must be last) ---
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Mount static files (JS, CSS, Images)
if os.path.exists("frontend/out"):
    app.mount("/_next", StaticFiles(directory="frontend/out/_next"), name="next")
    # app.mount("/static", StaticFiles(directory="frontend/out/static"), name="static") # If you have a static folder

    # Catch-all for SPA routing (serve index.html)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Check if file exists in out directory (e.g. favicon.ico)
        file_path = os.path.join("frontend/out", full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Otherwise return index.html
        return FileResponse("frontend/out/index.html")

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
