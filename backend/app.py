from fastapi import FastAPI
from pydantic import BaseModel
from email_agent.tool import fetch_lastest_emails
import uuid
from fastapi.middleware.cors import CORSMiddleware
from agent import Jarvis_Agent

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
agent = Jarvis_Agent()

class MessageRequest(BaseModel):
    message: str

@app.get("/fetch_latest_emails")
def fetch_emails():
    result = fetch_lastest_emails(10)
    if result:
        return {"emails": result}
    else:
        return {"emails": []}


@app.get("/agent/ask")
def talk_to_agent(message:MessageRequest):
    response = agent.call_agent(message.message)
    return {"response": response}
    