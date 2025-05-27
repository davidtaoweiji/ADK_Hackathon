from tool import fetch_lastest_emails,send_email,search_emails,reply_email,set_auto_reply,download_attachments
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
import asyncio
from google.genai import types
import json
import time
from common.agent_utils import pprint_events

APP_NAME = "hello_world_example"
USER_ID = "user12345"
SESSION_ID = "session12345"
AGENT_NAME = "hello_word_agent"
MODEL = "gemini-2.0-flash-001"

email_agent = Agent(
    model=MODEL,
    name="EmailAgent",
    tools=[fetch_lastest_emails, send_email, search_emails, reply_email, set_auto_reply, download_attachments],
    instruction=
    '''You are EmailAgent, an intelligent email management assistant. Your core functions include sending, retrieving, searching, handling attachments and auto-replies. Always follow these rules:

    == CORE PRINCIPLES ==
    1. CONFIRM BEFORE ACTION (except search/retrieving)
    - Any action except search/retrieve require explicit confirmation
    - Example: User says "Send this email" → Respond: "Confirm sending? (Yes/No)"

    2. CLARIFY INCOMPLETE REQUESTS
    - Missing parameters? Notice, in certain fuction not all parameter are needed. Ask relevant questions to gather necessary details.
    - Example: User says "Send email" → Ask: "To whom? Subject? Content?"

    == FUNCTIONS ==
    1. SEND EMAIL

    2. RETRIEVE RECENT EMAIL

    3. SEARCH EMAILS

    4. REPLY TO EMAIL

    5. SET UP OR MODIFY AUTO-REPLY
    
    6. DOWNLOAD ATTACHMENTS
    ''' 
)

# Session and Runner


def call_agent(runner, query):
  content = types.Content(role='user', parts=[types.Part(text=query)])
  events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
  return events
  # for event in events:
  #     if event.is_final_response():
  #         final_response = event.content.parts[0].text
  #         print("Agent Response: ", final_response)

if __name__ == "__main__":
    session_service = InMemorySessionService()
    session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=email_agent, app_name=APP_NAME, session_service=session_service)
    events = call_agent(runner, "hello, i want to see my latest emails")
    pprint_events(events)

