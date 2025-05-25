import os
import asyncio
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

import warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level = logging.ERROR)

print("Libraries imported successfully.")


os.environ["GOOGLE_API_KEY"] = ""
print("API Keys Set:")
print(f"GOOGLE_API_KEY: {"YES" if os.environ.get("GOOGLE_API_KEY") and os.environ.get("GOOGLE_API_KEY")!="YOUR_GOOGLE_API_KEY" else "NO (REPLACE PLACEHOLDER)"}")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"

MODEL_GEMINI_FLASH_2_0_FLASH = "gemini-2.0-flash"
print("\n ENVIRONMENT CONFIGURED")


# *****TOOL SETUP*****
def get_weather(city:str)-> dict:
    """
    Retreives the current weather report for a specified city
    
    Args:
        city(str): The name of the city (e.g., "New York", "london", "Tokyo")
        
    Returns:
        dict: A dictionary containing the weather information.
                includes a "status" key ("success" or "error"),
                If "success", includes a "report" key with the weather details.
                if "error", includes an "error_message" key.
    """
    print(f"---Tool: get weather called for the city: {city}---")
    city_normalized = city.lower().replace(" ", "_")
    
    Mock_weather_db = {
        "new_york":{"status":"success", "report":"The weather in New York is sunny with a temperature of 25°C."},
        "london":{"status":"success", "report":"The weather in London is cloudy with a temperature of 18°C."},
        "tokyo":{"status":"success", "report":"The weather in Tokyo is rainy with a temperature of 22°C."},
    }
    
    if city_normalized in Mock_weather_db:
        return Mock_weather_db[city_normalized]
    else:
        return{"status":"error", "error_message": f"No weather data available for {city}."}
    
print(get_weather("New York"))
print(get_weather("Paris"))

# *****AGENT SETUP*****
AGENT_MODEL = MODEL_GEMINI_FLASH_2_0_FLASH

weather_agent = Agent(
    name = "weather_agent_v1",
    model = AGENT_MODEL,
    description = "Provides weather information for specific cities.",
    instruction = "You are a helpful weather assistant."
                "When the user asks for the weather in a specified city, "
                " use the get_weather tool to retrieve the current weather report for that city. "
                " If the tool returns an error, inform the user politely"
                " If the tool is successful, present the weather report in a clear and concise manner.",
    tools = [get_weather],
)

print(f"\nAgent {weather_agent.name} created with the model {AGENT_MODEL}.")

# *****Setup Session Service *****

session_service = InMemorySessionService()
APP_NAME = "WeatherAgentApp"
USER_ID = "USER_1"
SESSION_ID = "session_001"



# *****Define Agent Interaction Function*****
async def call_agent_async(query: str, runner, user_id, session_id):
    """Sends a query to the agent and prints the final response."""
    print(f"\n---Calling an agent with query: {query}---")
    
    content = types.Content(role = "user", parts = [types.Part(text = query)])
    final_response_text = "Agent did not produce a final response."
    
    async for event in runner.run_async(user_id = user_id, session_id = session_id, new_message = content):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response_text = f"Agent escalated: {event.error_message or "No Specified Message" }"
            break
    print(f"\n---Final Response from Agent: {final_response_text}---")
    
    
# *****Run Conversation*****
async def run_conversation():
    session = await session_service.create_session(
        app_name = APP_NAME,
        user_id = USER_ID,
        session_id = SESSION_ID,
    )
    print(f"\nSession created: {SESSION_ID} for user {USER_ID} in app {APP_NAME}.")
    runner = Runner(
        agent = weather_agent,
        session_service = session_service,
        app_name = APP_NAME,
    )
    print(f"\nRunner created for agent {weather_agent.name} with session service {SESSION_ID}.")
    
    
    await call_agent_async("What is the weather in New York?", runner=runner, user_id=USER_ID, session_id=SESSION_ID)
    await call_agent_async("What is the weather in Paris?", runner=runner, user_id=USER_ID, session_id=SESSION_ID)
    await call_agent_async("What is the weather in London?", runner=runner, user_id=USER_ID, session_id=SESSION_ID)

# if __name__ == "__main__":
#     try:
#         asyncio.run(run_conversation())
#     except Exception as e:
#         print(f"An error occurred: {e}")
        

#*****Defining the tools for Greeting and Farewell Agents*****
def say_hello(name:str = "there") -> str:
    """Provides simplr greeting to the user, optionally along with their name.
    Args:
        name (str, optional): The name of the user, if providedd, else defaults to "there"
    Returns:
        str: A friendly greeting to the user.
    """
    print(f"---Tool: say_hello called with the name {name}---")
    return f"Hello, {name}! How may I help you today?"

def say_goodbye() -> str:
    """Provides a Farewell to the user upon conclusion of the conversation"""
    print(f"---Tool: say_goodbye called---")
    return "Goodbye! Have a great day ahead!"
    
print("Greeting and Farewell tools defined successfully.")

print(say_hello("Abhay"))
print(say_goodbye())
    

# *****Greeting agent creation***** 
greeting_agent = None
try:
    greeting_agent = Agent(
        name = "greeting_agent_v1",
        model = MODEL_GEMINI_FLASH_2_0_FLASH,
        description = "Handles simple greetings with the user, using the 'say_hello' tool",
        instruction = "You are a Greeting Agent. Your ONLY task is to greet the user." 
                    "Use the 'say_hello' tool to greet the user"
                    " If they provide their name, make sure to pass it to the tool."
                    "Do not engage in any other conversation or tasks.",
        tools = [say_hello],
    )
    print(f"\n greeting_agent created with the model {MODEL_GEMINI_FLASH_2_0_FLASH}.")
except Exception as e:
    print(f"Error creating Greeting Agent {e}")

# *****Farewell agent creation*****
farewell_agent = None
try:
    farewell_agent = Agent(
        name = "farewell_agent_v1",
        model = MODEL_GEMINI_FLASH_2_0_FLASH,
        description = "Handles simple farewells with the user, using the 'say_goodbye' tool",
        instruction = "You are a Farewell Agent. Your ONLY task is to bid farewell to the user." 
                    "Use the 'say_goodbye' tool to bid farewell to the user."
                    "Do not engage in any other conversation or tasks.",
        tools = [say_goodbye],
    )
    print(f"\n farewell_agent created with the model {MODEL_GEMINI_FLASH_2_0_FLASH}.")
except Exception as e:
    print(f"Error creating Farewell Agent {e}")
    
    
#*****Defining the Root Agent with Sub-Agents*****
root_agent = None
runner_root = None
if greeting_agent and farewell_agent and "get_weather" in globals():
    root_agent_model = MODEL_GEMINI_FLASH_2_0_FLASH
    
    weather_agent_team = Agent(
        name = "weather_agent_team_v1",
        model = root_agent_model,
        description = "THe main coordinating agent that handles the weather requests, and delegates greeting/farewell to the specialists.",
        instruction = "You are the main Weather Agent."
                    "Use the 'get_weather' tool ONLY for specific weather requests (e.g., 'weather in London'). "
                    "You have specialized sub-agents: "
                    "1. 'greeting_agent': Handles simple greetings like 'Hi', 'Hello'. Delegate to it for these. "
                    "2. 'farewell_agent': Handles simple farewells like 'Bye', 'See you'. Delegate to it for these. "
                    "Analyze the user's query. If it's a greeting, delegate to 'greeting_agent'. If it's a farewell, delegate to 'farewell_agent'. "
                    "If it's a weather request, handle it yourself using 'get_weather'. "
                    "For anything else, respond appropriately or state you cannot handle it.",
        tools = [get_weather, say_hello, say_goodbye],
        sub_agents = [greeting_agent, farewell_agent],
    )
    print(f"\n Root Agent {weather_agent_team.name} created with the model {root_agent_model} with sub-agents {[sa.name for sa in weather_agent_team.sub_agents]}.")
else:
    print("Cannot create root agent because one or more sub-agents failed to initialize or 'get_weather' tool is missing.")    
    if greeting_agent is None:
        print("Greeting agent is not initialized.")
    if farewell_agent is None:
        print("Farewell agent is not initialized.")
    if 'get_weather' not in globals():
        print("'get_weather' tool is not defined in the global scope.")

# *****Interact with the Agent Team*****
root_agent_var_name = "root_agent"
if 'weather_agent_team' in globals(): 
    root_agent_var_name = 'weather_agent_team'
elif 'root_agent' not in globals():
    print("Root agent ('root_agent' or 'weather_agent_team') not found. Cannot define run_team_conversation.")

if "weather_agent_team" in globals() and globals()[root_agent_var_name]:
    async def run_team_conversation():
        print("\n---Testing Agent Team Delegation---")
        session_service = InMemorySessionService()
        SESSION_ID =  "session_001_agent_team"
        USER_ID = "USER_1_agent_team"
        APP_NAME = "WeatherAgentApp_Team"
        session = await session_service.create_session(
            app_name = APP_NAME,
            user_id = USER_ID,
            session_id = SESSION_ID,
        )
        print(f"\nSession created: {SESSION_ID} for user {USER_ID} in app {APP_NAME}.")
        
        actual_root_agent = globals()[root_agent_var_name]
        runner_agent_team = Runner(
            agent = actual_root_agent,
            session_service = session_service,
            app_name = APP_NAME,
        )
        print(f"\nRunner created for agent {actual_root_agent.name} with session service {SESSION_ID}.")
    
        await call_agent_async("What is the weather in New York?", runner=runner_agent_team, user_id=USER_ID, session_id=SESSION_ID)
        await call_agent_async("Hello", runner=runner_agent_team, user_id=USER_ID, session_id=SESSION_ID)
        await call_agent_async("Bye", runner=runner_agent_team, user_id=USER_ID, session_id=SESSION_ID)
        await call_agent_async("Hey I'm Abhay", runner=runner_agent_team, user_id=USER_ID, session_id=SESSION_ID)        
        
        
    if __name__ == "__main__":
        try:
            asyncio.run(run_team_conversation())
        except Exception as e:
            print(f"An error occurred: {e}")
else:
    print(f"Cannot run team conversation because the root agent '{root_agent_var_name}' is not defined or initialized.")