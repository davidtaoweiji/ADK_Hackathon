from fastapi import FastAPI, Request
from pydantic import BaseModel
from email_agent.tool import fetch_lastest_emails
from calendar_agent.tool import get_events
from mobility_agent.tool import get_current_weather
from fastapi.middleware.cors import CORSMiddleware
from agent import Jarvis_Agent
from agent import root_agent
import uvicorn
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from common.agent_utils import start_agent_session, agent_to_client_sse
from fastapi.responses import RedirectResponse, StreamingResponse
from google.genai.types import Part, Content
from datetime import datetime, timedelta
import requests
import json
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from fastapi import Body

load_dotenv()

agent = Jarvis_Agent()
active_sessions = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("Starting up...")
    await agent.initialize()
    yield
    # Shutdown logic
    print("Shutting down...")
    # await disconnect_from_db()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MessageRequest(BaseModel):
    message: str


@app.get("/fetch_latest_emails")
def fetch_emails():
    result = fetch_lastest_emails(10)
    if result:
        return {"emails": result}
    else:
        return {"emails": []}


@app.get("/fetch_calendar_events")
def fetch_calendar():
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    result = get_events(start_date=today, end_date=tomorrow, max_results=10)
    if result:
        return {"events": result}
    else:
        return {"events": []}


@app.get("/fetch_weather")
def fetch_weather():
    # Placeholder for weather fetching logic
    # You can implement your weather fetching logic here
    weather = get_current_weather("Richardson, TX")
    return {"weather": weather}


@app.post("/agent/ask")
async def talk_to_agent(message: MessageRequest):
    response = await agent.call_agent(message.message)
    return {"response": response}


@app.get("/events/{user_id}")
async def sse_endpoint(user_id: int):
    """SSE endpoint for agent to client communication"""

    # Start agent session
    user_id_str = str(user_id)
    live_events, live_request_queue = await start_agent_session(
        user_id_str, "Jarvis Personal Assistant", root_agent
    )

    # Store the request queue for this user
    active_sessions[user_id_str] = live_request_queue

    def cleanup():
        live_request_queue.close()
        if user_id_str in active_sessions:
            del active_sessions[user_id_str]
        print(f"Client #{user_id} disconnected from SSE")

    async def event_generator():
        try:
            async for data in agent_to_client_sse(live_events):
                yield data
        except Exception as e:
            print(f"Error in SSE stream: {e}")
        finally:
            cleanup()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        },
    )


@app.post("/send/{user_id}")
async def send_message_endpoint(user_id: int, message: MessageRequest):
    """HTTP endpoint for client to agent communication"""

    user_id_str = str(user_id)

    # Get the live request queue for this user
    live_request_queue = active_sessions.get(user_id_str)
    if not live_request_queue:
        return {"error": "Session not found"}

    data = message.message

    # Send the message to the agent

    content = Content(role="user", parts=[Part.from_text(text=data)])
    live_request_queue.send_content(content=content)
    print(f"[CLIENT TO AGENT]: {data}")
    return {"status": "sent"}

@app.get("/oauth2callback")
def oauth2callback(request: Request, code: str = None, error: str = None):
    if not code:
        return {"error": "No code provided"}

    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/contacts",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    ])
    flow.redirect_uri = "http://127.0.0.1:8000/oauth2callback"
    try:
        flow.fetch_token(code=code)
    except Exception as e:
        return {"error": "Failed to fetch token", "details": str(e)}

    credentials = flow.credentials
    # Store credentials (for demo, write to a file; in production, use a secure store)
    creds_dict = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }
    with open("token.json", "w") as f:
        json.dump(creds_dict, f)

# Add this block to run the app directly
if __name__ == "__main__":
    uvicorn.run(
        "app:app", host="127.0.0.1", port=8000, reload=True
    )  # Add this block to run the app directly



