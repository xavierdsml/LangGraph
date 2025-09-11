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
    st.text(userInput)


  # ai message
  response = workflow.invoke(
    {'messages':[HumanMessage(content=userInput)]}, config={'configurable':{'thread_id':'1'}}
    )
  aiMessage = response['messages'][-1].content

  
  with st.chat_message('ai'):
    
    aiMessage = st.write_stream(
      message_chunk.content for message_chunk, metadata in workflow.stream(

        {'messages':[HumanMessage(content=userInput)]}, 
        config = {'configurable':{'thread_id':'1'}},
        stream_mode = 'messages'
      )
    )
  st.session_state['messageHistroy'].append({'role':'ai', 'content':aiMessage})