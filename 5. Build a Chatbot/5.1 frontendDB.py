import streamlit as st
from chatbotBackendDB import workflow
from langchain_core.messages import HumanMessage
import uuid 

# **************************************** Utility Functions *************************
def generateThreadId():
    return str(uuid.uuid4())

def resetChat():
    threadID = generateThreadId()
    st.session_state['threadID'] = threadID
    addThread(threadID)
    st.session_state['messageHistory'] = []
    st.session_state["chatTitles"][threadID] = f"Chat {len(st.session_state['chatThreads'])}"

def addThread(threadID):
    if threadID not in st.session_state['chatThreads']:
        st.session_state['chatThreads'].append(threadID)

def loadConversation(threadID):
    state = workflow.get_state(config={'configurable': {'thread_id': threadID}})
    return state.values.get('messages', [])


# **************************************** Session Setup ******************************
if 'messageHistory' not in st.session_state:
    st.session_state['messageHistory'] = []

if 'threadID' not in st.session_state:
    st.session_state['threadID'] = generateThreadId()

if 'chatThreads' not in st.session_state:
    st.session_state['chatThreads'] = []

if 'chatTitles' not in st.session_state:
    st.session_state['chatTitles'] = {}

addThread(st.session_state['threadID'])

if st.session_state['threadID'] not in st.session_state["chatTitles"]:
    st.session_state["chatTitles"][st.session_state['threadID']] = f"Chat {len(st.session_state['chatThreads'])}"


# **************************************** Sidebar UI *********************************
st.sidebar.title('LangGraph ChatBot')

if st.sidebar.button('New Chat', key="new_chat_btn"):
    resetChat()

st.sidebar.header('My Conversations')

for idx, threadID in enumerate(st.session_state['chatThreads'][::-1]):
    title = st.session_state["chatTitles"].get(threadID, str(threadID))
    if st.sidebar.button(title, key=f"thread_btn_{threadID}_{idx}"):
        st.session_state['threadID'] = threadID
        messages = loadConversation(threadID)

        tempMessages = []
        for msg in messages:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            tempMessages.append({'role': role, 'content': msg.content})

        st.session_state['messageHistory'] = tempMessages


# **************************************** Main UI ************************************
# loading the conversation history
for message in st.session_state['messageHistory']:
    with st.chat_message(message['role']):
        st.text(message['content'])

userInput = st.chat_input("Type here")

if userInput:

    # Add user message
    st.session_state['messageHistory'].append({'role': 'user', 'content': userInput})
    with st.chat_message('user'):
        st.text(userInput)

    # Auto-update chat title with first user message if it's still default
    currentThread = st.session_state['threadID']
    if st.session_state["chatTitles"].get(currentThread, "").startswith("Chat "):
        short_title = " ".join(userInput.split()[:6])
        st.session_state["chatTitles"][currentThread] = short_title

    CONFIG = {
        "configurable": {"thread_id": st.session_state["threadID"]},
        "metadata": {"thread_id": st.session_state["threadID"]},
        "run_name": "chat_turn",
    }

    # Assistant streaming response
    with st.chat_message('assistant'):
        aiMessage = st.write_stream(
            message_chunk.content
            for message_chunk, metadata in workflow.stream(
                {"messages": [HumanMessage(content=userInput)]},
                config=CONFIG,
                stream_mode="messages"
            )
        )

    st.session_state['messageHistory'].append({'role': 'assistant', 'content': aiMessage})