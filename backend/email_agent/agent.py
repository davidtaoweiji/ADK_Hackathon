from tool import fetch_lastest_emails,send_email,search_emails,reply_email,set_auto_reply,download_attachments
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
import asyncio
from google.genai import types
import json
import time
import os
from common.agent_utils import pprint_events

APP_NAME = "hello_world_example"
USER_ID = "user12345"
SESSION_ID = "session12345"
AGENT_NAME = "hello_word_agent"
MODEL = "gemini-2.5-flash-preview-05-20"

email_agent = Agent(
    model=MODEL,
    name="EmailAgent",
    tools=[fetch_lastest_emails, send_email, search_emails, reply_email, set_auto_reply, download_attachments],
    instruction=
    '''You are EmailAgent, an intelligent email management assistant. Your core functions include sending, retrieving, searching, handling attachments and auto-replies. Always follow these rules:

    == CORE PRINCIPLES ==
    1. CONFIRM BEFORE ACTION (except search/retrieving)
    - Any action except search or retrieve require explicit confirmation
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
    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)
    return events


# async def main():
#     API_KEY = "AIzaSyD6zVPESBqOyQ6tvtVbfHvhgm-dC3ikKC0"
#     os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE" # Use Vertex AI API
#     os.environ["GOOGLE_API_KEY"] = API_KEY
#     session_service = InMemorySessionService()
#     session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
#     runner = Runner(agent=email_agent, app_name=APP_NAME, session_service=session_service)
#     events = call_agent(runner, "hello, I want to send an email to jtw1091367152@qq.com, subject is 'test', content is 'this is a test email'.")
#     pprint_events(events)

# if __name__ == "__main__":
#     asyncio.run(main())
# async def main():
#     API_KEY = "AIzaSyD6zVPESBqOyQ6tvtVbfHvhgm-dC3ikKC0"
#     os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"
#     os.environ["GOOGLE_API_KEY"] = API_KEY
#     session_service = InMemorySessionService()
#     session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
#     runner = Runner(agent=email_agent, app_name=APP_NAME, session_service=session_service)
#     print("Type your message (type 'exit' to quit):")
#     while True:
#         user_input = input("> ")
#         if user_input.lower() == "exit":
#             break
#         events = call_agent(runner, user_input)
#         # pprint_events([events])

# if __name__ == "__main__":
#     asyncio.run(main())