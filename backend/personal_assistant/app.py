from fastapi import FastAPI
from pydantic import BaseModel
from email_agent.tool import fetch_lastest_emails
from fastapi.middleware.cors import CORSMiddleware
from agent import Jarvis_Agent
import uvicorn
from contextlib import asynccontextmanager

agent = Jarvis_Agent()
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


@app.post("/agent/ask")
async def talk_to_agent(message: MessageRequest):
    response = await agent.call_agent(message.message)
    return {"response": response}

# Add this block to run the app directly
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)# Add this block to run the app directly
