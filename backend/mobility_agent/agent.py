from tool import estimate_travel_time,recommend_entertainment_places,recommend_food_places, get_current_weather,get_future_weather,get_uber_link
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
import asyncio
from google.genai import types
from dotenv import load_dotenv

APP_NAME = "hello_world_example"
USER_ID = "user12345"
SESSION_ID = "session12345"
MODEL = "gemini-2.5-flash-preview-05-20"

mobility_agent = Agent(
    model=MODEL,
    name="MobilityAgent",
    tools=[estimate_travel_time, recommend_entertainment_places, recommend_food_places, get_current_weather,get_future_weather, get_uber_link],
    instruction=
    '''
    You are a smart assistant that helps users with mobility, entertainment, and food recommendations. 
    Use your available tools to answer user questions and provide helpful, concise, and actionable information. 
    Combine multiple tools when needed to fulfill complex requests. Always provide up-to-date and location-specific answers.
    You can provide information on travel times, recommend food and entertainment places, check the weather, and generate Uber links.
    If user asks for recommendations for food, make sure to tell user what are all the food types the function can search.
    If user asks for recommendations for entertainment, make sure to tell user what are all the entertainment type the function can search.
    ''' 
)

# def call_agent(runner, query):
#     content = types.Content(role='user', parts=[types.Part(text=query)])
#     events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
#     for event in events:
#         if event.is_final_response():
#             final_response = event.content.parts[0].text
#             print("Agent Response: ", final_response)
#     return events

# async def main():
#     load_dotenv()
#     session_service = InMemorySessionService()
#     session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
#     runner = Runner(agent=mobility_agent, app_name=APP_NAME, session_service=session_service)
#     print("Type your message (type 'exit' to quit):")
#     while True:
#         user_input = input("> ")
#         if user_input.lower() == "exit":
#             break
#         events = call_agent(runner, user_input)
        # pprint_events([events])

# if __name__ == "__main__":
#     asyncio.run(main())

# "hi, i am having dinner around CBRE Richardson, TX, give me some suggestion"