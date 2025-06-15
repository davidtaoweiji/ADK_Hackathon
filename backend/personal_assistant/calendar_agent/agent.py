from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai import types
from . import prompt
from .tool import (
    get_events,
    add_event,
    cancel_event,
    invite_attendee_to_event,
    respond_to_event,
    get_contact_info,
    add_contact_info,
)

MODEL = "gemini-2.5-flash-preview-05-20"

generate_content_config = types.GenerateContentConfig(
    temperature=0.2,
)

event_finder_agent = Agent(
    name="event_finder_agent",
    model=MODEL,
    description="A specialist agent that finds or creates a single, specific event and returns its ID.",
    instruction=prompt.EVENT_FINDER_AGENT_INSTR,
    tools=[get_events],
)

contact_info_agent = Agent(
    name="contact_info_agent",
    model=MODEL,
    description=("Use this tool to find the email of a person."),
    instruction=prompt.CONTACT_INFO_AGENT_INSTR,
    tools=[get_contact_info],
)

calendar_agent = Agent(
    name="calendar_agent",
    model=MODEL,
    description="A personal calendar assistant.",
    instruction=prompt.CALENDAR_AGENT_INSTR,
    tools=[
        get_events,
        add_event,
        cancel_event,
        respond_to_event,
        invite_attendee_to_event,
        add_contact_info,
        AgentTool(agent=contact_info_agent),
        AgentTool(agent=event_finder_agent),
    ],
    generate_content_config=generate_content_config,
)

root_agent = calendar_agent
