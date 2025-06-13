from personal_assistant.email_agent.agent import email_agent
from personal_assistant.mobility_agent.agent import mobility_agent
from personal_assistant.calendar_agent.agent import calendar_agent
from personal_assistant.prompt import get_agent_instruction
from dotenv import load_dotenv
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from datetime import datetime


load_dotenv()

APP_NAME = "hello_world_example"
USER_ID = "user12345"
SESSION_ID = "session12345"
MODEL = "gemini-2.5-flash-preview-05-20"

root_agent = Agent(
    model=MODEL,
    name="root_agent",
    sub_agents=[
        email_agent,
        mobility_agent,
        calendar_agent
    ],
    instruction=get_agent_instruction(),
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
                # responses = event.get_function_responses()
                # if responses:
                #     for response in responses:
                #         tool_name = response.name
                #         result_dict = response.response # The dictionary returned by the tool
                #         print(f"  Tool Result: {tool_name} -> {result_dict}")
                # if event.get_function_calls():
                #     print("Function Calls: ", event.get_function_calls())
                if event.is_final_response():
                    final_response = event.content.parts[0].text
                    print("Agent Response: ", final_response)
                    return final_response
        except Exception as e:
            # Handle any exceptions that occur during the agent call
            return "Error calling agent:" + str(e)


