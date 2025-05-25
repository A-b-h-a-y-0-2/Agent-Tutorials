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