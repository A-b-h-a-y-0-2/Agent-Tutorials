# *****Initialize New Session Service and State*****
from google.adk.sessions import InMemorySessionService
from google.adk.tools.tool_context import ToolContext
import warnings 
import logging
warnings.filterwarnings("ignore")
logging.basicConfig(level = logging.INFO)
async def main():
    session_service_stateful = InMemorySessionService()
    print(f"Session service initialized: {session_service_stateful}")

    SESSION_ID_STATEFUL = "session_stateful_001"
    USER_ID_STATEFUL = "user_stateful_001"
    APP_NAME = "Weather Agent Stateful" 
    initial_state = {"user_preference_unit": "Celsius"}

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

