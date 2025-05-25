# *****Initialize New Session Service and State*****
from google.adk.sessions import InMemorySessionService
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

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

