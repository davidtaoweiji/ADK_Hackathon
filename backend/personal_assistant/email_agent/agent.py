from personal_assistant.email_agent.tool import (
    fetch_lastest_emails,
    send_email,
    search_emails,
    reply_email,
    set_auto_reply,
    download_attachments,
)
from google.adk.agents import Agent

MODEL = "gemini-2.5-flash-preview-05-20"

email_agent = Agent(
    model=MODEL,
    name="email_agent",
    tools=[
        fetch_lastest_emails,
        send_email,
        search_emails,
        reply_email,
        set_auto_reply,
        download_attachments,
    ],
    instruction="""You are email_agent, an intelligent email management assistant. 
    Your core functions include sending, retrieving, searching, replying, download attachments and setup auto-replies. 
    **Once you complete one request from root_agent, always summarize and output the current state to the user, then transfer back to the root_agent.**

    == CORE PRINCIPLES ==
    1. CONFIRM BEFORE ACTION (except search/retrieving)
    - Any action except search or retrieve require explicit confirmation
    - Example: User says "Send this email" → Respond: "Confirm sending? (Yes/No)"

    2. CLARIFY INCOMPLETE REQUESTS
    - Missing parameters? Notice, in certain fuction not all parameter are needed. Ask relevant questions to gather necessary details.
    - Example: User says "Send email" → Ask: "To whom? Subject? Content?"

    """,
)
