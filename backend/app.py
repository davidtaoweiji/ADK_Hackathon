from fastapi import FastAPI
from pydantic import BaseModel
from email_agent.tool import fetch_lastest_emails
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from dotenv import load_dotenv
from google.genai import types
import uuid
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
APP_NAME = "hello_world_example"
USER_ID = "user12345"
SESSION_ID = "session12345"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Set up session and runner once at startup

session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
# interactive_runner = Runner(agent=email_agent, app_name=APP_NAME, session_service=session_service)
# email_runner = Runner(agent=email_agent, app_name=APP_NAME)

class MessageRequest(BaseModel):
    message: str

def call_agent(runner, query):
    # Generate a unique session_id for each request (stateless)
    session_id = str(uuid.uuid4())
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=session_id, new_message=content)
    return events

@app.get("/fetch_latest_emails")
def fetch_emails():
    result = fetch_lastest_emails(10)
    if result:
        return {"emails": result}
    else:
        return {"emails": []}