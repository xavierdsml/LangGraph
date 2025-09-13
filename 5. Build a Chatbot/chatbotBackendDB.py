from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage

from typing import TypedDict, Annotated
import sqlite3
from dotenv import load_dotenv
load_dotenv()


# gemini model
chatLLM = ChatGoogleGenerativeAI(
  model='gemini-2.0-flash',
  temperature=0.5
)

# State formation
class chatBotLLmState(TypedDict):
  messages:Annotated[list[BaseMessage], add_messages]


# function for the state to execute the wok
def messageGen(state:chatBotLLmState)->chatBotLLmState:
  messageGene = state['messages']
  response = chatLLM.invoke(messageGene)
  return {'messages':[response]}


# Graph formation with inMemory
graph = StateGraph(chatBotLLmState)
graph.add_node('messageGen', messageGen)

graph.add_edge(START, 'messageGen')
graph.add_edge('messageGen', END)


# concept of the memory
conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
checkpointer=SqliteSaver(conn=conn)
workflow = graph.compile(checkpointer=checkpointer)


# extract the number of threads from db for frontend
def retriveAllThreads():
  allThreads = set()
  for checkpoint in checkpointer.list(None):
    allThreads.add(checkpoint.config['configurable']['thread_id'])

  return list(allThreads)