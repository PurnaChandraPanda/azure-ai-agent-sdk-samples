import streamlit as st
import asyncio
from _foundry_agent import FoundryAgent

async def agent_api_invoke(prompt):
    # Call the async founder agent API
    _foundry_agent = await FoundryAgent.create()

    # The async context manager guarantees the aiohttp session and connector are closed before the event loop shuts down, eliminating the runtime warnings and allowing response to be printed normally.
    # Interact with _foundry_agent as needed
    async with _foundry_agent.lifecycle():
        return await _foundry_agent.run(prompt)

def process_prompt():
    """
    Process the user input prompt and display a response.
    """
    prompt = st.session_state.get("prompt", "").strip()
    if prompt:
        with st.spinner("Processing..."):
            # API interaction to get the response; blocking call
            agent_response = asyncio.run(agent_api_invoke(prompt))
        
        response = f"Prompt: {prompt}, Response: {agent_response}"

        # Initialize chat history if not present
        if "chat" not in st.session_state:
            st.session_state["chat"] = []
        
        st.session_state.chat.append({"prompt": prompt, "response": response})
        
        # Optionally clear the text_input after submission
        st.session_state.prompt = ""
    else:
        st.error("Please provide a valid prompt.")

st.title("Azure AI Agent SDK Samples - Agents Web App UI")

st.text_input(
    "Enter your prompt here:",
    key="prompt",
    on_change=process_prompt
)

# Display chat history below in reverse order
if "chat" in st.session_state:
    st.markdown("### Chat History")
    # Iterate in reverse order (latest message first)
    for msg in reversed(st.session_state.chat):
        st.write(msg["response"])