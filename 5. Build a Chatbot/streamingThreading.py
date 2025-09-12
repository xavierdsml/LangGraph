import streamlit as st
from chatbotBackend import workflow
from langchain_core.messages import HumanMessage
import uuid 

# ************************ Utility Functions ******************
def generateThreadId():
    return str(uuid.uuid4())

def resetChat():
    threadId = generateThreadId()
    st.session_state['threadID'] = threadId
    addThread(threadId)
    st.session_state['messageHistory'] = []
    st.session_state["chatTitles"][threadId] = f"Chat {len(st.session_state['chatThreads'])}"

def addThread(threadID):
    if threadID not in st.session_state['chatThreads']:
        st.session_state['chatThreads'].append(threadID)

def loadConversation(threadID):
    state = workflow.get_state(config={'configurable': {'thread_id': threadID}})
    return state.values.get('messages', [])


# ***************************** Session Setup ************************************
if 'messageHistory' not in st.session_state:
    st.session_state['messageHistory'] = []

if 'threadID' not in st.session_state:
    st.session_state['threadID'] = generateThreadId()
  
if 'chatThreads' not in st.session_state:
    st.session_state['chatThreads'] = []

if "chatTitles" not in st.session_state:
    st.session_state["chatTitles"] = {}

addThread(st.session_state['threadID'])
if st.session_state['threadID'] not in st.session_state["chatTitles"]:
    st.session_state["chatTitles"][st.session_state['threadID']] = f"Chat {len(st.session_state['chatThreads'])}"


# ***************************************** Side UI************************************
st.sidebar.title('LangGraph ChatBot')

if st.sidebar.button('New Chat'):
    resetChat()

st.sidebar.header('My Conversations')

# Show list of chats with friendly names
for threadID in st.session_state['chatThreads'][::-1]:
    title = st.session_state["chatTitles"].get(threadID, str(threadID))
    if st.sidebar.button(title):
        st.session_state['threadID'] = threadID
        messages = loadConversation(threadID)

        tempMessages = []
        for msg in messages:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            tempMessages.append({'role': role, 'content': msg.content})
        
        st.session_state['messageHistory'] = tempMessages


# ************************************** Main UI *****************************
# load the conversation history
for message in st.session_state['messageHistory']:
    with st.chat_message(message['role']):
        st.text(message['content'])

# message input -> CHAT
userInput = st.chat_input()
if userInput:

    # user message
    st.session_state['messageHistory'].append({'role': 'user', 'content': userInput})
    with st.chat_message('user'):
        st.text(userInput)

    # Auto-update chat title with first user message if it's still default
    currentThread = st.session_state['threadID']
    if st.session_state["chatTitles"].get(currentThread, "").startswith("Chat "):
        # Use first 6 words as a short title
        short_title = " ".join(userInput.split()[:6])
        st.session_state["chatTitles"][currentThread] = short_title

    CONFIG = {'configurable': {'thread_id': st.session_state['threadID']}}

    with st.chat_message('assistant'):
        response_collector = {"text": ""}

        def stream_response():
            for message_chunk, metadata in workflow.stream(
                {"messages": [HumanMessage(content=userInput)]},
                config=CONFIG,
                stream_mode="messages"
            ):
                content = message_chunk.content
                response_collector["text"] += content
                yield content

        st.write_stream(stream_response())
        aiMessage = response_collector["text"]

    st.session_state['messageHistory'].append({'role': 'assistant', 'content': aiMessage})