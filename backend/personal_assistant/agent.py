from personal_assistant.email_agent.agent import email_agent
from personal_assistant.mobility_agent.agent import mobility_agent
from personal_assistant.calendar_agent.agent import calendar_agent
from personal_assistant.prompt import get_agent_instruction
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from datetime import datetime


APP_NAME = "Jarvis Personal Assistant"
USER_ID = "user12345"
SESSION_ID = "session12345"
MODEL = "gemini-2.5-flash-preview-05-20"


generate_content_config = types.GenerateContentConfig(
    temperature=0.2,
)

root_agent = Agent(
    model=MODEL,
    name="root_agent",
    sub_agents=[email_agent, mobility_agent, calendar_agent],
    instruction=get_agent_instruction(),
    generate_content_config=generate_content_config,
)


class Jarvis_Agent:
    def __init__(self):
        pass

    async def initialize(self):
        self.session_service = InMemorySessionService()
        self.session = await self.session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )
        self.jarvis_agent = root_agent
        self.runner = Runner(
            agent=self.jarvis_agent,
            app_name=APP_NAME,
            session_service=self.session_service,
        )

    async def call_agent(self, query):
        if not self.session:
            return "Error: Session not initialized. Please call `initialize` first."
        try:
            current_timestamp = datetime.now().isoformat()
            content = types.Content(role="user", parts=[types.Part(text=query)])
            events = self.runner.run(
                user_id=USER_ID, session_id=SESSION_ID, new_message=content
            )
            for event in events:
                if event.is_final_response():
                    final_response = event.content.parts[0].text
                    print("Agent Response: ", final_response)
                    return final_response
        except Exception as e:
            # Handle any exceptions that occur during the agent call
            return "Error calling agent:" + str(e)
