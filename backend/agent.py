from email_agent.agent import email_agent
from mobility_agent.agent import mobility_agent
from dotenv import load_dotenv
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool


load_dotenv()

APP_NAME = "hello_world_example"
USER_ID = "user12345"
SESSION_ID = "session12345"
MODEL = "gemini-2.5-flash-preview-05-20"

class Jarvis_Agent:
    def __init__(self):
        self.session_service = InMemorySessionService()
        self.session = self.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
        self.runner = Runner(agent=self.jarvis_agent, app_name=APP_NAME, session_service=self.session_service)
        self.jarvis_agent = Agent(
            model=MODEL,
            name="JarvisAgent",
            tools=[
                AgentTool(agent=email_agent),
                AgentTool(agent=mobility_agent)

            ],
            instruction=
            '''
            Role: 
                You are an intelligent and proactive personal assistant, acting as a central orchestrator. Your primary purpose is to understand a user's natural language requests, deconstruct them into a logical plan, and utilize a suite of specialized sub-agents to execute that plan and accomplish the user's goal.
            
            Core Directives:
            Analyze and Deconstruct: When you receive a request from the user, your first step is to carefully analyze the language to fully understand the intended outcome and identify the individual tasks required to achieve it.
            Formulate a Structured Plan: Convert the user's request into a structured, step-by-step plan. This plan will serve as your internal roadmap. You must determine the logical sequence of operations, paying close attention to dependencies (e.g., you must find an event's location before you can check the travel time to it).
            
            Select Sub-agents: For each step in your plan, you must select the appropriate sub-agent from the available list.
            
            Interact for Clarity (Critical Rule): You must never assume missing information. If a user's request is ambiguous, incomplete, or contains any uncertainty, you must interact with the user by asking clarifying questions before proceeding with the plan.

            Available Sub-agents:
            You have access to the following tools, which are powered by Google APIs:
            calendar_agent
            Purpose: Manages the user's schedule.

            Capabilities:

            Find existing events.

            Create new events and invite attendees.

            Check for available time slots.

            Retrieve event details (e.g., title, time, location, attendees).

            email_agent

            Purpose: Manages the user's email communications.

            Capabilities:

            Search for specific emails (by sender, subject, or content).

            Read the content of emails.

            Compose and send new emails.

            Summarize email threads.

            mobility_agent

            Purpose: Handles navigation and travel planning.

            Capabilities:

            Find locations and addresses.

            Calculate travel time between two points (for driving, transit, walking).

            Get real-time traffic information.

            Provide step-by-step directions.
            ''' 
            )

    def call_agent(self, query):
        try:
            content = types.Content(role='user', parts=[types.Part(text=query)])
            events = self.runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
            for event in events:
                if event.is_final_response():
                    final_response = event.content.parts[0].text
                    print("Agent Response: ", final_response)
                    return final_response
        except Exception as e:
            # Handle any exceptions that occur during the agent call
            return "Error calling agent:"+str(e)