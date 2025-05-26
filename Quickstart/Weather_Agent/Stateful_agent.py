# *****Initialize New Session Service and State*****
from google.adk.sessions import InMemorySessionService
from google.adk.tools.tool_context import ToolContext
from google.adk.agents import Agent
from google.adk.runners import Runner 
import os
import warnings 
import logging
warnings.filterwarnings("ignore")
logging.basicConfig(level = logging.INFO)

# *****Define constants and environment variables*****
os.environ["GOOGLE_API_KEY"] = ""
print("API Keys Set:")
print(f"GOOGLE_API_KEY: {"YES" if os.environ.get("GOOGLE_API_KEY") and os.environ.get("GOOGLE_API_KEY")!="YOUR_GOOGLE_API_KEY" else "NO (REPLACE PLACEHOLDER)"}")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"

MODEL_GEMINI_FLASH_2_0_FLASH = "gemini-2.0-flash"
print("\n ENVIRONMENT CONFIGURED")

SESSION_ID_STATEFUL = "session_stateful_001"
USER_ID_STATEFUL = "user_stateful_001"
APP_NAME = "Weather Agent Stateful" 
initial_state = {"user_preference_unit": "Celsius"}
session_service_stateful = InMemorySessionService()
print(f"Session service initialized: {session_service_stateful}")


#*****# Define a stateful agent that can maintain session state*****
async def main():

    session_stateful = await session_service_stateful.create_session(
        app_name = APP_NAME,
        session_id=SESSION_ID_STATEFUL,
        user_id=USER_ID_STATEFUL,
        state=initial_state
    )
    print(f"Session created: {SESSION_ID_STATEFUL} for user {USER_ID_STATEFUL} in app {APP_NAME}")

    retrieved_session = await session_service_stateful.get_session(app_name = APP_NAME,
        session_id=SESSION_ID_STATEFUL,
        user_id=USER_ID_STATEFUL)


    print("\n INITIAL SESSION STATE: ")
    if retrieved_session:
        print(retrieved_session.state)
    else:
        print("ERROR: Session not found.")
        
    

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())

# *****# Define a state-aware tool to retrieve weather information*****
def get_weather_stateful(city: str, tool_context: ToolContext)-> dict:
    """ Retrieves weather information, converts units based on user preference and based on session state"""
    print(f"---TOOL: get_weather_stateful called for {city}")
    preferred_unit = tool_context.state.get("user_preference_unit", "Celsius")
    print(f"---Tool: Reading state 'user_preference_unit' : {preferred_unit}")
    
    city_normalized = city.lower().replace(" ","_")
    
    mock_weather_db = {
        "new_york":{"temperature_celsius": 22, "condition": "sunny"},
        "london":{"temperature_celsius": 25, "condition": "windy"},
        "tokyo":{"temperature_celsius": 30, "condition": "rainy"},
    }
    
    if city_normalized in mock_weather_db:
        weather_data = mock_weather_db[city_normalized]
        temp_c = weather_data["temperature_celsius"]
        condition = weather_data["condition"]
        
        if preferred_unit == "Fahrenheit":
            temp_value =(9/5) * temp_c + 32
            temp_unit = "°F"
            
        else:
            temp_value = temp_c
            temp_unit = "°C"
        
        report = f"The weather in {city.capitalize()} is {condition} with a temperture {temp_value}{temp_unit}"
        result = {"status": "success", "report": report}
        print(f"---Tool: Generated report in {preferred_unit}. Result: {result}---")
        
        tool_context.state["last_city_checked_stateful"] = city
        print(f"---Tool: Updated session state with last city checked: {city}---")
        
        return result
    else:
        error_message = f"City {city} not found in mock database."
        print(f"---Tool: {error_message}---")
        return {"status": "error", "message": error_message}
print("State-aware 'get_weather_stateful' tool defined.")


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

# print(say_hello("Abhay"))
# print(say_goodbye())

# *****Redefine Sub-Agents and Update Root Agent with output key
AGENT_MODEL = MODEL_GEMINI_FLASH_2_0_FLASH
greeting_agent = None
try:
    greeting_agent = Agent(
        name = "greeting_agent_stateful_v1",
        model = AGENT_MODEL,
        description = "Handles simple greetings and hellos using the 'say_hello' tool.",
        instruction = "You are the Greeting Agent. Your ONLY task is to provide a friendly greeting using the 'say_hello' tool. Do nothing else.",
        tools = [say_hello],
    )
    print(f"Agent: {greeting_agent.name} redefined successfully.")
except Exception as e:
    print(f"Error defining greeting agent: {e}")
    
farewell_agent = None
try:
    farewell_agent = Agent(
        model=AGENT_MODEL,
        name="farewell_agent",
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message using the 'say_goodbye' tool. Do not perform any other actions.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
        tools=[say_goodbye],
    )
    print(f"✅ Agent '{farewell_agent.name}' redefined successfully.")
except Exception as e:
    print(f"Error defining Farewell agent: {e}")

root_agent_stateful = None
runner_root_stateful = None

if greeting_agent and farewell_agent and "get_weather_stateful" in globals():
    root_agent_model = AGENT_MODEL
    root_agent_stateful = Agent(
        name = "root_agent_stateful_v1",
        model = root_agent_model,
        description = "coordinates between greeting, farewell, and weather tools.",
        instruction="You are the main Weather Agent. Your job is to provide weather using 'get_weather_stateful'. "
                    "The tool will format the temperature based on user preference stored in state. "
                    "Delegate simple greetings to 'greeting_agent' and farewells to 'farewell_agent'. "
                    "Handle only weather requests, greetings, and farewells.",
        tools = [get_weather_stateful],
        sub_agents = [greeting_agent, farewell_agent],
        output_key = "last_weather_report", #Auto-save agent's final weather response

    )
    print(f"✅ Root Agent '{root_agent_stateful.name}' redefined successfully with output key 'last_weather_report'.")

    runner = Runner(
        agent = root_agent_stateful,
        session_service = session_service_stateful,
        app_name = APP_NAME,
    )
    print(f"Runner initialized for agent: {runner.agent.name} with session service: {SESSION_ID_STATEFUL}")
else:
    print("Error: Unable to initialize root agent or runner. Ensure all agents and tools are defined correctly.")
    if not greeting_agent:
        print("Greeting agent is not defined.")
    if not farewell_agent:
        print("Farewell agent is not defined.")
    if "get_weather_stateful" not in globals():
        print("Weather tool 'get_weather_stateful' is not defined.")


