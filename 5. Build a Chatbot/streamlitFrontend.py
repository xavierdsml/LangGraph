import streamlit as st
from chatbotBackend import workflow
from langchain_core.messages import HumanMessage

# messageHistory maintained by the help of the session_state
if 'messageHistroy' not in st.session_state:
  st.session_state['messageHistroy'] = []

# loading the converstion history
for message in st.session_state['messageHistroy']:
  with st.chat_message(message['role']):
    # st.text(message['content'])
    st.markdown(message['content'])



# message input -> CHAT
userInput = st.chat_input()
if(userInput):

  # user message
  st.session_state['messageHistroy'].append({'role':'user', 'content':userInput})
  with st.chat_message('user'):
    # st.text(userInput)
    st.markdown(userInput)


  # ai message
  response = workflow.invoke(
    {'messages':[HumanMessage(content=userInput)]}, config={'configurable':{'thread_id':'1'}}
    )
  aiMessage = response['messages'][-1].content

  st.session_state['messageHistroy'].append({'role':'ai', 'content':aiMessage})
  with st.chat_message('ai'):
    st.text(aiMessage)